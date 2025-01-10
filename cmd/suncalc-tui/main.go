package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"sort"
	"time"

	"github.com/charmbracelet/bubbles/list"
	"github.com/charmbracelet/bubbles/spinner"
	"github.com/charmbracelet/bubbles/textinput"
	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/lipgloss"
)

// Model states
const (
	stateLocationSelect = iota
	stateCoordinateInput
	stateDateInput
	stateCalculating
	stateResults
)

// Keyboard shortcuts help text
const (
	locationHelp = "↑/↓: navigate • /: filter • enter: select • h: help • q: quit"
	dateHelp     = "enter: confirm (or empty for today) • t: today • h: help • esc: back • q: quit"
	resultsHelp  = "r: recalculate • n: new search • h: help • q: quit"
)

// City data structures
type CityData struct {
	Latitude  float64 `json:"latitude"`
	Longitude float64 `json:"longitude"`
	Timezone  string  `json:"timezone"`
}

type Cities map[string]CityData

// API types
type CalculationRequest struct {
	Name      string  `json:"name"`
	Latitude  float64 `json:"latitude"`
	Longitude float64 `json:"longitude"`
	Date      string  `json:"date"`
}

type CalculationResponse struct {
	SunriseUTC string `json:"sunrise_utc"`
	SunsetUTC  string `json:"sunset_utc"`
}

// City item for the list
type cityItem struct {
	name      string
	latitude  float64
	longitude float64
	timezone  string
}

func (i cityItem) Title() string       { return i.name }
func (i cityItem) Description() string { 
	return fmt.Sprintf("Lat: %.4f, Lon: %.4f, TZ: %s", i.latitude, i.longitude, i.timezone) 
}
func (i cityItem) FilterValue() string { return i.name }

// Main model
type model struct {
	state     int
	cityList  list.Model
	latitude  textinput.Model
	longitude textinput.Model
	date      textinput.Model
	spinner   spinner.Model
	err       error
	styles    struct {
		title   lipgloss.Style
		input   lipgloss.Style
		results lipgloss.Style
		help    lipgloss.Style
		error   lipgloss.Style
	}
	showHelp bool

	// Selected values
	selectedCity  *cityItem
	selectedLat   float64
	selectedLon   float64
	selectedDate  string

	// Calculation results
	sunriseUTC string
	sunsetUTC  string
}

func loadCities() ([]list.Item, error) {
	file, err := os.ReadFile("cities.json")
	if err != nil {
		execPath, err := os.Executable()
		if err != nil {
			return nil, fmt.Errorf("failed to get executable path: %v", err)
		}
		file, err = os.ReadFile(filepath.Join(filepath.Dir(execPath), "cities.json"))
		if err != nil {
			return nil, fmt.Errorf("failed to read cities.json: %v", err)
		}
	}

	var cities Cities
	if err := json.Unmarshal(file, &cities); err != nil {
		return nil, fmt.Errorf("failed to parse cities.json: %v", err)
	}

	items := make([]list.Item, 0, len(cities))
	for name, data := range cities {
		items = append(items, cityItem{
			name:      name,
			latitude:  data.Latitude,
			longitude: data.Longitude,
			timezone:  data.Timezone,
		})
	}

	sort.Slice(items, func(i, j int) bool {
		return items[i].(cityItem).name < items[j].(cityItem).name
	})

	return items, nil
}

func startCalculatorServer() error {
	cmd := exec.Command("python", "calculator_server.py")
	if err := cmd.Start(); err != nil {
		return fmt.Errorf("failed to start calculator server: %v", err)
	}
	time.Sleep(2 * time.Second)
	return nil
}

func calculateSunTimes(m model) tea.Cmd {
	return func() tea.Msg {
		req := CalculationRequest{
			Name:      m.selectedCity.name,
			Latitude:  m.selectedLat,
			Longitude: m.selectedLon,
			Date:      m.selectedDate,
		}

		jsonData, err := json.Marshal(req)
		if err != nil {
			return fmt.Errorf("failed to marshal request: %v", err)
		}

		resp, err := http.Post("http://localhost:8080/calculate", "application/json", bytes.NewBuffer(jsonData))
		if err != nil {
			return fmt.Errorf("failed to call API: %v", err)
		}
		defer resp.Body.Close()

		if resp.StatusCode != http.StatusOK {
			return fmt.Errorf("API returned status %d", resp.StatusCode)
		}

		var result CalculationResponse
		if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
			return fmt.Errorf("failed to decode response: %v", err)
		}

		return result
	}
}

func initialModel() model {
	if err := startCalculatorServer(); err != nil {
		fmt.Printf("Warning: Failed to start calculator server: %v\n", err)
	}

	// Initialize text inputs
	lat := textinput.New()
	lat.Placeholder = "Latitude (-90 to 90)"
	lat.CharLimit = 10
	lat.Width = 20

	lon := textinput.New()
	lon.Placeholder = "Longitude (-180 to 180)"
	lon.CharLimit = 11
	lon.Width = 20

	date := textinput.New()
	date.Placeholder = "YYYY-MM-DD"
	date.CharLimit = 10
	date.Width = 20

	// Initialize spinner
	s := spinner.New()
	s.Spinner = spinner.Dot
	s.Style = lipgloss.NewStyle().Foreground(lipgloss.Color("#FFD700"))

	// Load cities
	items, err := loadCities()
	if err != nil {
		items = []list.Item{} // Empty list if loading fails
	}

	// Initialize list
	cityList := list.New(items, list.NewDefaultDelegate(), 0, 0)
	cityList.Title = "Select a City"
	cityList.SetShowHelp(true)
	cityList.SetFilteringEnabled(true)
	cityList.SetShowStatusBar(true)

	m := model{
		state:     stateLocationSelect,
		cityList:  cityList,
		latitude:  lat,
		longitude: lon,
		date:      date,
		spinner:   s,
		err:       err,
	}

	// Set initial theme
	hour := time.Now().Hour()
	m.styles = getThemeStyles(hour)
	m.cityList.Styles.Title = m.styles.title

	return m
}

func (m model) Init() tea.Cmd {
	return tea.Batch(textinput.Blink, m.spinner.Tick)
}

func (m model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	var cmd tea.Cmd
	var cmds []tea.Cmd

	switch msg := msg.(type) {
	case tea.KeyMsg:
		switch msg.String() {
		case "ctrl+c", "q":
			return m, tea.Quit
		case "h":
			m.showHelp = !m.showHelp
			return m, nil
		case "esc":
			if m.showHelp {
				m.showHelp = false
				return m, nil
			}
			if m.state > stateLocationSelect {
				m.state--
				if m.state == stateLocationSelect {
					m.selectedCity = nil
				}
				return m, nil
			}
		case "n":
			if m.state == stateResults {
				m.state = stateLocationSelect
				m.selectedCity = nil
				return m, nil
			}
		case "r":
			if m.state == stateResults {
				m.state = stateCalculating
				return m, tea.Batch(
					calculateSunTimes(m),
					m.spinner.Tick,
				)
			}
		case "t":
			if m.state == stateDateInput {
				m.selectedDate = time.Now().Format("2006-01-02")
				m.state = stateCalculating
				return m, tea.Batch(
					calculateSunTimes(m),
					m.spinner.Tick,
				)
			}
		case "enter":
			switch m.state {
			case stateLocationSelect:
				if i, ok := m.cityList.SelectedItem().(cityItem); ok {
					m.selectedCity = &i
					m.selectedLat = i.latitude
					m.selectedLon = i.longitude
					m.state = stateDateInput
					m.date.Focus()
					return m, textinput.Blink
				}
			case stateCoordinateInput:
				// TODO: Validate coordinates
				m.state = stateDateInput
				m.date.Focus()
				return m, textinput.Blink
			case stateDateInput:
				if m.date.Value() == "" {
					m.selectedDate = time.Now().Format("2006-01-02")
				} else {
					_, err := time.Parse("2006-01-02", m.date.Value())
					if err != nil {
						m.err = fmt.Errorf("invalid date format: use YYYY-MM-DD")
						return m, nil
					}
					m.selectedDate = m.date.Value()
				}
				m.state = stateCalculating
				return m, tea.Batch(
					calculateSunTimes(m),
					m.spinner.Tick,
				)
			}
		}

	case CalculationResponse:
		m.sunriseUTC = msg.SunriseUTC
		m.sunsetUTC = msg.SunsetUTC
		m.state = stateResults
		return m, nil

	case error:
		m.err = msg
		if m.state == stateCalculating {
			m.state = stateDateInput
		}
		return m, nil

	case tea.WindowSizeMsg:
		h, v := m.styles.input.GetFrameSize()
		m.cityList.SetSize(msg.Width-h, msg.Height-v)

	case spinner.TickMsg:
		var cmd tea.Cmd
		m.spinner, cmd = m.spinner.Update(msg)
		return m, cmd
	}

	// Handle state-specific updates
	switch m.state {
	case stateLocationSelect:
		m.cityList, cmd = m.cityList.Update(msg)
		return m, cmd

	case stateCoordinateInput:
		if m.latitude.Focused() {
			m.latitude, cmd = m.latitude.Update(msg)
			cmds = append(cmds, cmd)
		} else {
			m.longitude, cmd = m.longitude.Update(msg)
			cmds = append(cmds, cmd)
		}
		return m, tea.Batch(cmds...)

	case stateDateInput:
		m.date, cmd = m.date.Update(msg)
		return m, cmd
	}

	return m, nil
}

func (m model) View() string {
	if m.showHelp {
		return m.helpView()
	}

	var s string

	switch m.state {
	case stateLocationSelect:
		s = m.styles.title.Render("Sun Calculator") + "\n\n" +
			m.cityList.View() + "\n\n" +
			m.styles.help.Render(locationHelp)

	case stateCoordinateInput:
		s = m.styles.title.Render("Enter Coordinates") + "\n\n" +
			m.styles.input.Render(m.latitude.View()) + "\n" +
			m.styles.input.Render(m.longitude.View()) + "\n\n" +
			m.styles.help.Render("tab: switch field • enter: confirm • esc: back • q: quit")

	case stateDateInput:
		title := "Enter Date"
		if m.selectedCity != nil {
			title += fmt.Sprintf(" for %s", m.selectedCity.name)
		}
		s = m.styles.title.Render(title) + "\n\n" +
			m.styles.input.Render(m.date.View()) + "\n\n" +
			m.styles.help.Render(dateHelp)

	case stateCalculating:
		s = m.styles.title.Render("Calculating...") + "\n\n"
		s += m.spinner.View() + " "
		if m.selectedCity != nil {
			s += fmt.Sprintf("Calculating sun times for %s\n", m.selectedCity.name)
		}
		s += fmt.Sprintf("Coordinates: %.4f, %.4f\n", m.selectedLat, m.selectedLon)
		s += fmt.Sprintf("Date: %s\n", m.selectedDate)

	case stateResults:
		title := "Results"
		if m.selectedCity != nil {
			title += fmt.Sprintf(" for %s", m.selectedCity.name)
		}

		// Get current hour to determine which ASCII art to show
		hour := time.Now().Hour()
		var art string
		if hour >= 6 && hour < 20 {
			art = sunArt
		} else {
			art = moonArt
		}

		s = m.styles.title.Render(title) + "\n\n" +
			m.styles.results.Render(
				lipgloss.JoinVertical(lipgloss.Center,
					art,
					fmt.Sprintf(
						"Date: %s\n"+
							"Coordinates: %.4f°, %.4f°\n"+
							"Sunrise: %s\n"+
							"Sunset: %s",
						m.selectedDate,
						m.selectedLat, m.selectedLon,
						m.sunriseUTC,
						m.sunsetUTC,
					),
				),
			) + "\n\n" +
			m.styles.help.Render(resultsHelp)
	}

	if m.err != nil {
		s += "\n\n" + m.styles.error.Render(m.err.Error())
	}

	return s
}

func (m model) helpView() string {
	help := `
Keyboard Shortcuts:

Navigation
----------
↑/↓: Move selection up/down
enter: Select/Confirm
esc: Go back/Cancel
q: Quit application

City Selection
-------------
/: Filter cities
enter: Select city

Date Input
----------
t: Use today's date
enter: Confirm date (empty for today)

Results View
-----------
r: Recalculate
n: New search

General
-------
h: Toggle this help
q: Quit
`
	return m.styles.title.Render("Help") + "\n" +
		m.styles.results.Render(help) + "\n\n" +
		m.styles.help.Render("press h to return")
}

func main() {
	p := tea.NewProgram(initialModel())
	if _, err := p.Run(); err != nil {
		fmt.Printf("Error running program: %v", err)
		os.Exit(1)
	}
}

package main

import "github.com/charmbracelet/lipgloss"

// Theme colors
var (
	sunriseColors = struct {
		primary   lipgloss.Color
		secondary lipgloss.Color
		accent    lipgloss.Color
		text      lipgloss.Color
	}{
		primary:   lipgloss.Color("#FF8C00"),  // Deep Orange
		secondary: lipgloss.Color("#FFD700"),  // Gold
		accent:    lipgloss.Color("#FFA07A"),  // Light Salmon
		text:      lipgloss.Color("#FFFFFF"),  // White
	}

	dayColors = struct {
		primary   lipgloss.Color
		secondary lipgloss.Color
		accent    lipgloss.Color
		text      lipgloss.Color
	}{
		primary:   lipgloss.Color("#87CEEB"),  // Sky Blue
		secondary: lipgloss.Color("#FFD700"),  // Gold
		accent:    lipgloss.Color("#98FB98"),  // Pale Green
		text:      lipgloss.Color("#000000"),  // Black
	}

	sunsetColors = struct {
		primary   lipgloss.Color
		secondary lipgloss.Color
		accent    lipgloss.Color
		text      lipgloss.Color
	}{
		primary:   lipgloss.Color("#FF6B6B"),  // Sunset Red
		secondary: lipgloss.Color("#FFB347"),  // Pastel Orange
		accent:    lipgloss.Color("#FFE4B5"),  // Moccasin
		text:      lipgloss.Color("#FFFFFF"),  // White
	}
)

// ASCII art
const (
	sunArt = `
    \\   |   //
     \\  |  //
      \\ | //
   -----(*)-----
      // | \\
     //  |  \\
    //   |   \\
`

	moonArt = `
      _...._
    .:::::::.
   :::::::::::
   :::::::::::
   ':::::::::' 
     ':::::' 
       ':'
`
)

// Theme styles based on time of day
func getThemeStyles(hour int) struct {
	title   lipgloss.Style
	input   lipgloss.Style
	results lipgloss.Style
	help    lipgloss.Style
	error   lipgloss.Style
} {
	var colors struct {
		primary   lipgloss.Color
		secondary lipgloss.Color
		accent    lipgloss.Color
		text      lipgloss.Color
	}

	// Select color scheme based on time
	switch {
	case hour >= 5 && hour < 8: // Sunrise
		colors = sunriseColors
	case hour >= 8 && hour < 17: // Day
		colors = dayColors
	case hour >= 17 && hour < 20: // Sunset
		colors = sunsetColors
	default: // Night
		colors = sunsetColors // Use sunset colors for night
	}

	return struct {
		title   lipgloss.Style
		input   lipgloss.Style
		results lipgloss.Style
		help    lipgloss.Style
		error   lipgloss.Style
	}{
		title: lipgloss.NewStyle().
			Bold(true).
			Foreground(colors.primary).
			Border(lipgloss.RoundedBorder()).
			BorderForeground(colors.secondary).
			Padding(1),

		input: lipgloss.NewStyle().
			Border(lipgloss.RoundedBorder()).
			BorderForeground(colors.accent).
			Padding(0, 1),

		results: lipgloss.NewStyle().
			Border(lipgloss.DoubleBorder()).
			BorderForeground(colors.primary).
			Padding(1),

		help: lipgloss.NewStyle().
			Foreground(colors.accent),

		error: lipgloss.NewStyle().
			Foreground(lipgloss.Color("#FF0000")),
	}
}
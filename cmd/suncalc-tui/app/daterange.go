package main

import (
	"fmt"
	"time"

	"suncalc-tui/pkg/astrotime"
)

// DateRange represents a range of dates for calculation
type DateRange struct {
	Start     time.Time
	End       time.Time
	Current   time.Time
	RangeType string
}

// RangeType constants
const (
	RangeThreeDay   = "3-day"
	RangeWeek       = "1-week"
	RangeTwoWeek    = "2-week"
	RangeThreeWeek  = "3-week"
	RangeMonth      = "month"
)

// NewDateRange creates a new date range of the specified type starting from the given date.
// Returns an error if the range exceeds allowed limits (±1 year from now).
func NewDateRange(start time.Time, rangeType string) (DateRange, error) {
	var end time.Time
	switch rangeType {
	case RangeThreeDay:
		end = start.AddDate(0, 0, 2) // 3 days including start
	case RangeWeek:
		end = start.AddDate(0, 0, 6) // 7 days including start
	case RangeTwoWeek:
		end = start.AddDate(0, 0, 13) // 14 days including start
	case RangeThreeWeek:
		end = start.AddDate(0, 0, 20) // 21 days including start
	case RangeMonth:
		end = start.AddDate(0, 1, -1) // Until end of month
	default:
		end = start // Single day
	}

	// Validate range is within allowed limits
	now := time.Now()
	minDate := now.AddDate(-1, 0, 0)
	maxDate := now.AddDate(1, 0, 0)

	if start.Before(minDate) {
		return DateRange{}, fmt.Errorf("date range starts too far in past (maximum 1 year ago)")
	}
	if end.After(maxDate) {
		return DateRange{}, fmt.Errorf("date range ends too far in future (maximum 1 year ahead)")
	}

	return DateRange{
		Start:     start,
		End:       end,
		Current:   start,
		RangeType: rangeType,
	}, nil
}

// Next moves to the next date in the range
func (dr *DateRange) Next() bool {
	if dr.Current.Before(dr.End) {
		dr.Current = dr.Current.AddDate(0, 0, 1)
		return true
	}
	return false
}

// Reset moves back to the start of the range
func (dr *DateRange) Reset() {
	dr.Current = dr.Start
}

// FormatRange returns a string representation of the date range
func (dr DateRange) FormatRange() string {
	if dr.Start.Equal(dr.End) {
		return dr.Start.Format("2006-01-02")
	}
	return fmt.Sprintf("%s to %s", 
		dr.Start.Format("2006-01-02"),
		dr.End.Format("2006-01-02"))
}

// DaysInRange returns the number of days in the range
func (dr DateRange) DaysInRange() int {
	return int(dr.End.Sub(dr.Start).Hours()/24) + 1
}

// NextRange returns a new range of the same type starting from the end of this range
func (dr DateRange) NextRange() DateRange {
	return NewDateRange(dr.End.AddDate(0, 0, 1), dr.RangeType)
}

// PrevRange returns a new range of the same type ending at the start of this range
func (dr DateRange) PrevRange() DateRange {
	var start time.Time
	switch dr.RangeType {
	case RangeThreeDay:
		start = dr.Start.AddDate(0, 0, -3)
	case RangeWeek:
		start = dr.Start.AddDate(0, 0, -7)
	case RangeTwoWeek:
		start = dr.Start.AddDate(0, 0, -14)
	case RangeThreeWeek:
		start = dr.Start.AddDate(0, 0, -21)
	case RangeMonth:
		start = dr.Start.AddDate(0, -1, 0)
	default:
		start = dr.Start.AddDate(0, 0, -1)
	}
	return NewDateRange(start, dr.RangeType)
}

// DateRangeResults stores calculation results for a date range
type DateRangeResults struct {
	Date       time.Time
	SunriseUTC string
	SunsetUTC  string
}

// CalculateResults calculates sun times for the current date in the range
func (dr DateRange) CalculateResults(latitude, longitude float64) DateRangeResults {
	sunrise := astrotime.CalcSunrise(dr.Current, latitude, longitude)
	sunset := astrotime.CalcSunset(dr.Current, latitude, longitude)
	
	return DateRangeResults{
		Date:       dr.Current,
		SunriseUTC: sunrise.UTC().Format("15:04:05 MST"),
		SunsetUTC:  sunset.UTC().Format("15:04:05 MST"),
	}
}

// FormatResults formats the results for display
func (dr DateRangeResults) Format() string {
	return fmt.Sprintf("%s:\n  Sunrise: %s\n  Sunset:  %s",
		dr.Date.Format("2006-01-02"),
		dr.SunriseUTC,
		dr.SunsetUTC)
}
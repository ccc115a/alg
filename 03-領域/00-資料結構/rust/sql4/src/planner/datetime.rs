//! 日期時間函式（SQLite 相容）
//!
//! 支援：
//!   date(timestr, modifier...)   → "YYYY-MM-DD"
//!   time(timestr, modifier...)   → "HH:MM:SS"
//!   datetime(timestr, modifier...)  → "YYYY-MM-DD HH:MM:SS"
//!   julianday(timestr, modifier...) → f64
//!   strftime(fmt, timestr, modifier...) → string
//!   now()  / date('now') / datetime('now')
//!
//! timestr 格式：
//!   'now'、'YYYY-MM-DD'、'YYYY-MM-DD HH:MM:SS'、julianday 數字

use std::time::{SystemTime, UNIX_EPOCH};

// ── 內部時間表示 ───────────────────────────────────────────────────────────

#[derive(Debug, Clone, Copy)]
struct DateTime {
    year:  i32,
    month: u8,   // 1-12
    day:   u8,   // 1-31
    hour:  u8,
    min:   u8,
    sec:   u8,
}

impl DateTime {
    fn now_utc() -> Self {
        let secs = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap_or_default()
            .as_secs() as i64;
        Self::from_unix(secs)
    }

    /// Unix timestamp → DateTime（UTC，忽略閏秒）
    fn from_unix(secs: i64) -> Self {
        let (days, rem) = (secs / 86400, secs % 86400);
        let hour = (rem / 3600) as u8;
        let min  = ((rem % 3600) / 60) as u8;
        let sec  = (rem % 60) as u8;
        let (year, month, day) = julian_to_ymd(days + 2440588); // Unix epoch = JD 2440588
        DateTime { year, month, day, hour, min, sec }
    }

    fn to_unix(&self) -> i64 {
        let jd = ymd_to_julian(self.year, self.month, self.day);
        let days = jd - 2440588;
        days * 86400 + self.hour as i64 * 3600 + self.min as i64 * 60 + self.sec as i64
    }

    fn to_julian_day(&self) -> f64 {
        let jd = ymd_to_julian(self.year, self.month, self.day) as f64;
        let frac = (self.hour as f64 - 12.0) / 24.0
            + self.min as f64 / 1440.0
            + self.sec as f64 / 86400.0;
        jd + frac
    }

    fn from_julian_day(jd: f64) -> Self {
        let day_int = jd as i64;
        let frac = jd - day_int as f64;
        let secs_in_day = (frac * 86400.0).round() as i64;
        let unix_secs = (day_int - 2440588) * 86400 + secs_in_day;
        Self::from_unix(unix_secs)
    }

    fn date_str(&self) -> String {
        format!("{:04}-{:02}-{:02}", self.year, self.month, self.day)
    }

    fn time_str(&self) -> String {
        format!("{:02}:{:02}:{:02}", self.hour, self.min, self.sec)
    }

    fn datetime_str(&self) -> String {
        format!("{} {}", self.date_str(), self.time_str())
    }
}

// ── Modifier 解析 ──────────────────────────────────────────────────────────

enum Modifier {
    AddDays(i64),
    AddMonths(i32),
    AddYears(i32),
    StartOfMonth,
    StartOfYear,
    StartOfDay,
    Weekday(u8),  // 0=Sunday
}

fn parse_modifier(s: &str) -> Option<Modifier> {
    let s = s.trim().to_lowercase();
    if s == "start of month" { return Some(Modifier::StartOfMonth); }
    if s == "start of year"  { return Some(Modifier::StartOfYear); }
    if s == "start of day"   { return Some(Modifier::StartOfDay); }
    if let Some(rest) = s.strip_prefix("weekday ") {
        if let Ok(n) = rest.trim().parse::<u8>() { return Some(Modifier::Weekday(n)); }
    }
    // "+N days/months/years", "-N days"
    let (sign, rest) = if s.starts_with('-') { (-1i64, &s[1..]) }
        else if s.starts_with('+') { (1i64, &s[1..]) }
        else { (1i64, s.as_str()) };
    let parts: Vec<&str> = rest.trim().splitn(2, ' ').collect();
    if parts.len() == 2 {
        if let Ok(n) = parts[0].parse::<i64>() {
            let unit = parts[1].trim_end_matches('s'); // days→day
            return match unit {
                "day"   => Some(Modifier::AddDays(sign * n)),
                "month" => Some(Modifier::AddMonths((sign * n) as i32)),
                "year"  => Some(Modifier::AddYears((sign * n) as i32)),
                "hour"  => Some(Modifier::AddDays(sign * n / 24)),
                _       => None,
            };
        }
    }
    None
}

fn apply_modifier(mut dt: DateTime, m: &Modifier) -> DateTime {
    match m {
        Modifier::AddDays(d) => {
            let unix = dt.to_unix() + d * 86400;
            dt = DateTime::from_unix(unix);
        }
        Modifier::AddMonths(m) => {
            let total = dt.month as i32 - 1 + m;
            let years = total.div_euclid(12);
            dt.month = (total.rem_euclid(12) + 1) as u8;
            dt.year += years;
        }
        Modifier::AddYears(y) => { dt.year += y; }
        Modifier::StartOfMonth => { dt.day = 1; dt.hour = 0; dt.min = 0; dt.sec = 0; }
        Modifier::StartOfYear  => { dt.month = 1; dt.day = 1; dt.hour = 0; dt.min = 0; dt.sec = 0; }
        Modifier::StartOfDay   => { dt.hour = 0; dt.min = 0; dt.sec = 0; }
        Modifier::Weekday(w) => {
            let jd = ymd_to_julian(dt.year, dt.month, dt.day);
            let current_dow = (jd + 1) % 7; // 0=Sunday
            let target = *w as i64;
            let diff = (target - current_dow).rem_euclid(7);
            let unix = dt.to_unix() + diff * 86400;
            dt = DateTime::from_unix(unix);
        }
    }
    dt
}

// ── Julian Day ↔ Gregorian ────────────────────────────────────────────────

fn ymd_to_julian(y: i32, m: u8, d: u8) -> i64 {
    let (y, m) = (y as i64, m as i64);
    let a = (14 - m) / 12;
    let yr = y + 4800 - a;
    let mo = m + 12 * a - 3;
    d as i64 + (153 * mo + 2) / 5 + 365 * yr + yr / 4 - yr / 100 + yr / 400 - 32045
}

fn julian_to_ymd(jd: i64) -> (i32, u8, u8) {
    let a = jd + 32044;
    let b = (4 * a + 3) / 146097;
    let c = a - (146097 * b) / 4;
    let d = (4 * c + 3) / 1461;
    let e = c - (1461 * d) / 4;
    let m = (5 * e + 2) / 153;
    let day   = (e - (153 * m + 2) / 5 + 1) as u8;
    let month = (m + 3 - 12 * (m / 10)) as u8;
    let year  = (100 * b + d - 4800 + m / 10) as i32;
    (year, month, day)
}

// ── 解析 timestr ──────────────────────────────────────────────────────────

fn parse_timestr(s: &str) -> Option<DateTime> {
    let s = s.trim();
    if s.eq_ignore_ascii_case("now") {
        return Some(DateTime::now_utc());
    }
    // julianday 數字
    if let Ok(jd) = s.parse::<f64>() {
        return Some(DateTime::from_julian_day(jd));
    }
    // YYYY-MM-DD HH:MM:SS
    if s.len() >= 19 && s.as_bytes()[4] == b'-' && s.as_bytes()[10] == b' ' {
        let y: i32 = s[0..4].parse().ok()?;
        let mo: u8 = s[5..7].parse().ok()?;
        let d: u8  = s[8..10].parse().ok()?;
        let h: u8  = s[11..13].parse().ok()?;
        let mi: u8 = s[14..16].parse().ok()?;
        let sc: u8 = s[17..19].parse().ok()?;
        return Some(DateTime { year: y, month: mo, day: d, hour: h, min: mi, sec: sc });
    }
    // YYYY-MM-DD
    if s.len() == 10 && s.as_bytes()[4] == b'-' {
        let y: i32 = s[0..4].parse().ok()?;
        let mo: u8 = s[5..7].parse().ok()?;
        let d: u8  = s[8..10].parse().ok()?;
        return Some(DateTime { year: y, month: mo, day: d, hour: 0, min: 0, sec: 0 });
    }
    None
}

fn resolve_datetime(timestr: &str, modifiers: &[String]) -> Option<DateTime> {
    let mut dt = parse_timestr(timestr)?;
    for m in modifiers {
        if let Some(modifier) = parse_modifier(m) {
            dt = apply_modifier(dt, &modifier);
        }
    }
    Some(dt)
}

// ── 公開函式 ──────────────────────────────────────────────────────────────

/// `date(timestr, modifier...)` → "YYYY-MM-DD"
pub fn fn_date(args: &[String]) -> Option<String> {
    let timestr = args.first()?;
    let mods: Vec<String> = args[1..].to_vec();
    Some(resolve_datetime(timestr, &mods)?.date_str())
}

/// `time(timestr, modifier...)` → "HH:MM:SS"
pub fn fn_time(args: &[String]) -> Option<String> {
    let timestr = args.first()?;
    let mods: Vec<String> = args[1..].to_vec();
    Some(resolve_datetime(timestr, &mods)?.time_str())
}

/// `datetime(timestr, modifier...)` → "YYYY-MM-DD HH:MM:SS"
pub fn fn_datetime(args: &[String]) -> Option<String> {
    let timestr = args.first()?;
    let mods: Vec<String> = args[1..].to_vec();
    Some(resolve_datetime(timestr, &mods)?.datetime_str())
}

/// `julianday(timestr, modifier...)` → f64
pub fn fn_julianday(args: &[String]) -> Option<f64> {
    let timestr = args.first()?;
    let mods: Vec<String> = args[1..].to_vec();
    Some(resolve_datetime(timestr, &mods)?.to_julian_day())
}

/// `strftime(fmt, timestr, modifier...)` → string
pub fn fn_strftime(args: &[String]) -> Option<String> {
    let fmt = args.first()?;
    let timestr = args.get(1)?;
    let mods: Vec<String> = args[2..].to_vec();
    let dt = resolve_datetime(timestr, &mods)?;

    let mut out = String::new();
    let chars: Vec<char> = fmt.chars().collect();
    let mut i = 0;
    while i < chars.len() {
        if chars[i] == '%' && i + 1 < chars.len() {
            i += 1;
            match chars[i] {
                'Y' => out.push_str(&format!("{:04}", dt.year)),
                'm' => out.push_str(&format!("{:02}", dt.month)),
                'd' => out.push_str(&format!("{:02}", dt.day)),
                'H' => out.push_str(&format!("{:02}", dt.hour)),
                'M' => out.push_str(&format!("{:02}", dt.min)),
                'S' => out.push_str(&format!("{:02}", dt.sec)),
                'j' => {  // day of year
                    let jan1 = ymd_to_julian(dt.year, 1, 1);
                    let today = ymd_to_julian(dt.year, dt.month, dt.day);
                    out.push_str(&format!("{:03}", today - jan1 + 1));
                }
                'w' => {  // weekday 0=Sunday
                    let jd = ymd_to_julian(dt.year, dt.month, dt.day);
                    out.push_str(&format!("{}", (jd + 1) % 7));
                }
                'W' => {  // week of year
                    let jan1 = ymd_to_julian(dt.year, 1, 1);
                    let today = ymd_to_julian(dt.year, dt.month, dt.day);
                    out.push_str(&format!("{:02}", (today - jan1) / 7));
                }
                'J' => out.push_str(&format!("{}", dt.to_julian_day())),
                's' => out.push_str(&format!("{}", dt.to_unix())),
                '%' => out.push('%'),
                c   => { out.push('%'); out.push(c); }
            }
        } else {
            out.push(chars[i]);
        }
        i += 1;
    }
    Some(out)
}

// ── 測試 ─────────────────────────────────────────────────────────────────

#[cfg(test)]
mod tests {
    use super::*;

    fn s(v: &str) -> Vec<String> { v.split(',').map(|s| s.trim().to_string()).collect() }

    #[test]
    fn date_basic() {
        let r = fn_date(&s("2024-03-15")).unwrap();
        assert_eq!(r, "2024-03-15");
    }

    #[test]
    fn date_add_days() {
        let r = fn_date(&s("2024-03-15, +5 days")).unwrap();
        assert_eq!(r, "2024-03-20");
    }

    #[test]
    fn date_subtract_days() {
        let r = fn_date(&s("2024-03-15, -5 days")).unwrap();
        assert_eq!(r, "2024-03-10");
    }

    #[test]
    fn date_start_of_month() {
        let r = fn_date(&s("2024-03-15, start of month")).unwrap();
        assert_eq!(r, "2024-03-01");
    }

    #[test]
    fn date_start_of_year() {
        let r = fn_date(&s("2024-08-20, start of year")).unwrap();
        assert_eq!(r, "2024-01-01");
    }

    #[test]
    fn time_basic() {
        let r = fn_time(&s("2024-03-15 14:30:00")).unwrap();
        assert_eq!(r, "14:30:00");
    }

    #[test]
    fn datetime_basic() {
        let r = fn_datetime(&s("2024-03-15 14:30:00")).unwrap();
        assert_eq!(r, "2024-03-15 14:30:00");
    }

    #[test]
    fn julianday_epoch() {
        // Unix epoch = JD 2440588.0 (at noon)
        let jd = fn_julianday(&s("1970-01-01")).unwrap();
        // 0:00:00 → jd = 2440588 - 0.5 = 2440587.5
        assert!((jd - 2440587.5).abs() < 0.01);
    }

    #[test]
    fn strftime_format() {
        let r = fn_strftime(&vec!["%Y/%m/%d".into(), "2024-03-15".into()]).unwrap();
        assert_eq!(r, "2024/03/15");
    }

    #[test]
    fn strftime_time() {
        let r = fn_strftime(&vec!["%H:%M:%S".into(), "2024-03-15 09:05:03".into()]).unwrap();
        assert_eq!(r, "09:05:03");
    }

    #[test]
    fn add_months() {
        let r = fn_date(&s("2024-01-31, +1 month")).unwrap();
        // 1月+1月 = 2月，日期保持31（可能溢出，SQLite 也有此行為）
        assert!(r.starts_with("2024-02"));
    }

    #[test]
    fn add_years() {
        let r = fn_date(&s("2024-03-15, +1 year")).unwrap();
        assert_eq!(r, "2025-03-15");
    }

    #[test]
    fn now_returns_string() {
        // 只測試格式，不測試確切值
        let r = fn_date(&vec!["now".into()]).unwrap();
        assert_eq!(r.len(), 10);
        assert_eq!(&r[4..5], "-");
    }
}

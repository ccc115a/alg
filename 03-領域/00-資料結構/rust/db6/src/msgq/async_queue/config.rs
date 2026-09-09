//! Async queue configuration — queue config, retry strategy, backoff algorithm

/// Async queue configuration
///
/// - `max_delivery_count`: Max delivery count (excess goes to DLQ)
/// - `dlq_name`: Dead letter queue name (None disables DLQ)
/// - `message_ttl_secs`: Message time-to-live (seconds)
/// - `priority_enabled`: Whether priority ordering is enabled
#[derive(Debug, Clone)]
pub struct AsyncQueueConfig {
    pub max_delivery_count: u32,
    pub dlq_name: Option<String>,
    pub message_ttl_secs: Option<u64>,
    pub priority_enabled: bool,
}

impl Default for AsyncQueueConfig {
    fn default() -> Self {
        Self {
            max_delivery_count: 3,
            dlq_name: None,
            message_ttl_secs: None,
            priority_enabled: false,
        }
    }
}

/// Retry configuration
///
/// - `max_retries`: Maximum retry count
/// - `initial_delay_ms`: Initial delay (milliseconds)
/// - `max_delay_ms`: Maximum delay (milliseconds)
/// - `backoff_multiplier`: Backoff multiplier (delay multiplied by this each time)
#[derive(Debug, Clone)]
pub struct RetryConfig {
    pub max_retries: u32,
    pub initial_delay_ms: u64,
    pub max_delay_ms: u64,
    pub backoff_multiplier: f64,
}

impl Default for RetryConfig {
    fn default() -> Self {
        Self {
            max_retries: 3,
            initial_delay_ms: 100,
            max_delay_ms: 5000,
            backoff_multiplier: 2.0,
        }
    }
}

/// Retry an async operation with exponential backoff
///
/// Process:
/// 1. Execute the operation
/// 2. If it fails and max retries not reached, wait delay ms
/// 3. delay = delay × backoff_multiplier (but capped at max_delay_ms)
/// 4. Repeat until success or max retries reached
pub async fn with_retry<T, F, E>(
    config: RetryConfig,
    mut operation: F,
) -> Result<T, E>
where
    F: FnMut() -> Result<T, E>,
{
    let mut delay = config.initial_delay_ms;
    let mut attempts = 0;

    loop {
        match operation() {
            Ok(result) => return Ok(result),
            Err(e) => {
                attempts += 1;
                if attempts >= config.max_retries {
                    return Err(e);
                }
                tokio::time::sleep(std::time::Duration::from_millis(delay)).await;
                delay = (delay as f64 * config.backoff_multiplier) as u64;
                delay = delay.min(config.max_delay_ms);
            }
        }
    }
}

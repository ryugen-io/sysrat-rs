use std::cell::RefCell;

use tachyonfx::{Effect, EffectTimer, Interpolation, fx};

pub struct SplashState {
    pub effect: RefCell<Effect>,
    pub start_time: f64,
}

impl SplashState {
    pub fn new() -> Self {
        // Rainbow effect using HSL shift
        let timer = EffectTimer::from_ms(3000, Interpolation::Linear);
        // Shift hue by 360 degrees (full circle)
        let effect = fx::ping_pong(fx::hsl_shift_fg([360.0, 0.0, 0.0], timer));

        Self {
            effect: RefCell::new(effect),
            start_time: js_sys::Date::now(),
        }
    }
}

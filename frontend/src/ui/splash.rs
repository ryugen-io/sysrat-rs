use crate::state::AppState;
use ratzilla::ratatui::{
    Frame,
    layout::{Alignment, Rect},
    style::Style,
    widgets::{Block, Borders, Paragraph},
};
use tachyonfx::{Duration, EffectRenderer};

pub fn render(f: &mut Frame, state: &AppState, area: Rect) {
    let _theme = &state.current_theme;

    // We want to center the text in the area
    let menu_ascii = include_str!("../../assets/menu-text.ascii");

    let widget = Paragraph::new(menu_ascii)
        .alignment(Alignment::Center)
        .style(Style::default().fg(ratzilla::ratatui::style::Color::Red))
        .block(Block::default().borders(Borders::ALL).title(" Sysrat "));

    f.render_widget(widget, area);

    // Apply rainbow effect
    // We assume ~60fps for smoothness, passing 16ms delta
    // web_sys::console::log_1(&wasm_bindgen::JsValue::from_str(
    //     "[DEBUG] Rendering Splash Screen",
    // ));
    f.render_effect(
        &mut *state.splash.effect.borrow_mut(),
        area,
        Duration::from_millis(16),
    );
}

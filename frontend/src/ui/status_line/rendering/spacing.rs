use crate::{
    state::AppState,
    theme::ThemeConfig,
    ui::status_line::{
        components,
        config::{ComponentConfig, RowConfig},
    },
};
use ratzilla::ratatui::text::Span;

/// Render a row's components with intelligent spacing between them.
/// Only adds spaces between components that actually render (return Some).
pub fn render_row_with_spacing(
    row_config: &RowConfig,
    state: &AppState,
    theme: &ThemeConfig,
) -> Vec<Span<'static>> {
    let mut spans = vec![];
    let mut last_was_content = false;
    let mut is_first_component = true;

    for component_config in &row_config.components {
        if let Some(span) = components::render_component(component_config, state, theme) {
            let is_spacing = is_spacing_component(component_config);

            // Add leading space for first content component (alignment)
            if is_first_component && !is_spacing {
                spans.push(Span::raw(" "));
                is_first_component = false;
            }

            // Add space before this component if last one was also content
            // (but not for spacer/separator types which handle their own spacing)
            if last_was_content && !is_spacing {
                spans.push(Span::raw(" "));
            }

            spans.push(span);
            last_was_content = !is_spacing;
        }
    }

    spans
}

/// Check if a component is a spacing-related component (spacer, separator, text with only spaces).
fn is_spacing_component(component: &ComponentConfig) -> bool {
    match component {
        ComponentConfig::Spacer => true,
        ComponentConfig::Separator { .. } => true,
        ComponentConfig::Text { value, .. } => value.trim().is_empty(),
        _ => false,
    }
}

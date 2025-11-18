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
            let is_closing_paren = is_closing_parenthesis(component_config);

            // Add leading space for first content component (alignment)
            // BUT: Don't add if the component already starts with a space
            if is_first_component && !is_spacing && !starts_with_space(component_config) {
                spans.push(Span::raw(" "));
                is_first_component = false;
            }

            // Add space before this component if last one was also content
            // EXCEPT: Don't add space before closing parentheses
            if last_was_content && !is_spacing && !is_closing_paren {
                spans.push(Span::raw(" "));
            }

            spans.push(span);
            last_was_content = !is_spacing;
            if is_first_component {
                is_first_component = false;
            }
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

/// Check if a text component starts with a space (already has leading spacing).
fn starts_with_space(component: &ComponentConfig) -> bool {
    match component {
        ComponentConfig::Text { value, .. } => value.starts_with(' '),
        _ => false,
    }
}

/// Check if a component is a closing parenthesis (no space before it).
fn is_closing_parenthesis(component: &ComponentConfig) -> bool {
    match component {
        ComponentConfig::Text { value, .. } => value.trim() == ")",
        _ => false,
    }
}

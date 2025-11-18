use crate::theme;
use wasm_bindgen::prelude::*;
use web_sys::{Document, window};

/// Inject font configuration into the document
pub fn inject_font(doc: &Document, font_config: &theme::FontConfig) -> Result<(), JsValue> {
    let head = doc
        .head()
        .ok_or_else(|| JsValue::from_str("No head element found"))?;

    // Inject CDN link if provided
    if let Some(cdn_url) = &font_config.cdn_url {
        // Check if font link already exists (avoid duplicates)
        if doc.query_selector("#theme-font-link")?.is_none() {
            let link = doc.create_element("link")?;
            link.set_attribute("id", "theme-font-link")?;
            link.set_attribute("rel", "stylesheet")?;
            link.set_attribute("href", cdn_url)?;
            head.append_child(&link)?;
        }
    }

    // Inject or update font style with proper icon rendering settings
    let style_id = "theme-font-style";
    let font_style = format!(
        "pre {{ \
            font-family: '{}', {}; \
            font-size: {}px; \
            font-weight: {}; \
            margin: 0; \
            font-variant-ligatures: none; \
            font-feature-settings: normal; \
            text-rendering: optimizeLegibility; \
            letter-spacing: 0; \
            line-height: 1.2; \
        }}",
        font_config.family, font_config.fallback, font_config.size, font_config.weight
    );

    if let Some(existing_style) = doc.get_element_by_id(style_id) {
        // Update existing style
        existing_style.set_inner_html(&font_style);
    } else {
        // Create new style element
        let style = doc.create_element("style")?;
        style.set_id(style_id);
        style.set_inner_html(&font_style);
        head.append_child(&style)?;
    }

    Ok(())
}

/// Update DOM elements (background + font) for theme changes
pub fn update_dom_for_theme(theme: &theme::ThemeConfig) -> Result<(), JsValue> {
    let win = window().ok_or_else(|| JsValue::from_str("No window"))?;
    let doc = win
        .document()
        .ok_or_else(|| JsValue::from_str("No document"))?;
    let body = doc.body().ok_or_else(|| JsValue::from_str("No body"))?;

    // Set background color
    let mantle = theme.mantle();
    if let ratzilla::ratatui::style::Color::Rgb(r, g, b) = mantle {
        let bg_color = format!("rgb({}, {}, {})", r, g, b);
        body.set_attribute("style", &format!("background-color: {}", bg_color))?;
    }

    // Inject font configuration
    inject_font(&doc, &theme.font)?;

    Ok(())
}

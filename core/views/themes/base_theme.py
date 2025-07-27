import gradio as gr

from gradio.themes.utils import colors, fonts, sizes

base_theme = gr.themes.Base(
    primary_hue=colors.blue,
    secondary_hue=colors.slate,
    font=fonts.GoogleFont("Inter"),
    spacing_size=sizes.spacing_md,
    radius_size=sizes.radius_md,
    text_size=sizes.text_md,
).set(
    body_background_fill="#f9f9fb",  # Very light gray
    body_text_color="#1f2937",  # Slate-800
    body_text_weight="400",  # Normal
    button_primary_background_fill=colors.indigo,  # Rich indigo blue
    button_primary_text_color="white",
    button_primary_border_color=colors.indigo,
    button_secondary_background_fill="#e5e7eb",  # Gray-200
    button_secondary_text_color="#1f2937",
    button_secondary_border_color="#d1d5db",  # Gray-300
    block_border_color="#e5e7eb",  # Subtle block borders
    block_background_fill="#ffffff",  # Clean white panels
    input_background_fill="#ffffff",
    input_border_color="#d1d5db",  # Light gray borders
    shadow_drop="shadow-md",  # Medium shadow
    shadow_drop_lg="shadow-lg",  # On hover
    link_text_color=colors.blue,
)

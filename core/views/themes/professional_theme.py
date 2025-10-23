"""
Professional theme for views in PostWizard

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

import gradio as gr
from gradio.themes.utils import colors, fonts, sizes

professional_theme = gr.themes.Base(
    # Core hues
    primary_hue=colors.teal,  # calming yet confident
    secondary_hue=colors.gray,  # neutral anchor
    # Typography & geometry
    font=fonts.GoogleFont("Lato"),  # elegant, highly legible
    spacing_size=sizes.spacing_md,  # balanced padding
    radius_size=sizes.radius_sm,  # subtle rounding
    text_size=sizes.text_md,  # comfortable reading
).set(
    # Page
    body_background_fill="#ffffff",  # crisp white canvas
    body_text_color="#1a1a1a",  # dark charcoal
    body_text_weight="400",
    # Primary button
    button_primary_background_fill=colors.teal,
    button_primary_border_color=colors.teal,
    button_primary_text_color="white",
    # Hover state
    button_primary_background_fill_hover="#138b7b",
    button_primary_border_color_hover="#138b7b",
    button_primary_text_color_hover="white",
    # Interaction
    button_transition="background-color 0.2s ease, transform 0.1s ease",
    button_transform_hover="scale(1.02)",
    # Secondary button
    button_secondary_background_fill="#f3f4f6",  # light gray
    button_secondary_border_color="#d1d5db",
    button_secondary_text_color="#4b5563",
    button_secondary_background_fill_hover="#e5e7eb",
    button_secondary_border_color_hover="#9ca3af",
    button_secondary_text_color_hover="#1f2937",
    # Inputs & selects
    input_background_fill="white",
    input_border_color="#d1d5db",
    input_radius=sizes.radius_sm,
    input_shadow="none",
    # Cards / panels
    block_background_fill="#fafafa",
    block_border_color="#e5e7eb",
    shadow_drop="shadow-sm",
)

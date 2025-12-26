# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2025 Yoham Gabriel B.

"""
Elegant theme for views in PostWizard

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

import gradio as gr
from gradio.themes.utils import colors, fonts, sizes

elegant_theme = gr.themes.Base(
    primary_hue=colors.purple,  # Jewel-tone purple
    secondary_hue=colors.cyan,  # Vibrant cyan accent
    font=fonts.GoogleFont("Poppins"),  # Geometric, modern font
    spacing_size=sizes.spacing_lg,  # More generous spacing
    radius_size=sizes.radius_lg,  # Softer, larger corners
    text_size=sizes.text_md,  # Comfortable readability
).set(
    body_background_fill="#ffffff",  # Clean white canvas
    body_text_color="#2c2c2c",  # Dark charcoal text
    body_text_weight="400",
    button_primary_background_fill_hover="#7e22ce",  # deep purple
    button_primary_border_color_hover="#7e22ce",  # match border
    button_primary_text_color_hover="white",
    button_secondary_background_fill_hover="#06b6d4",  # darker cyan
    button_secondary_border_color_hover="#06b6d4",
    button_secondary_text_color_hover="white",
    block_background_fill="#fbfbfb",  # Very light grey panels
    block_border_color="#e2e2e2",  # Soft panel outlines
    input_background_fill="white",
    input_border_color="#d1d5db",
    shadow_drop="shadow-lg",  # Deeper default shadows
    shadow_drop_lg="shadow-xl",  # Stronger hover shadows
    link_text_color=colors.cyan,
    button_transition="transform 0.2s ease, box-shadow 0.2s ease",
    button_transform_hover="translateY(-3px)",
    button_primary_shadow_hover="shadow-xl",
)

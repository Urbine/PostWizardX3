"""
PostDirector - Workflow Tweaks View

This module defines the Gradio interface for managing workflow tweaks.
It allows users to set up various tweaks and configurations for workflows present in PostDirector.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

import logging
import os
from pathlib import Path

# Third-party imports
import gradio as gr

from core.controllers.config_controller import (
    collect_config_state,
    load_config_fields,
    repair_from_template,
)
# Local imports

from core.views.themes import elegant_theme
from core import logging_setup

with gr.Blocks(
    theme=elegant_theme, title=" PostDirector - Workflow Tweaks"
) as conf_mgr:
    gr.Markdown("# PostDirector - Workflow Settings")
    with gr.Row():
        with gr.Column():
            with gr.Tab("Basic Settings"):
                gr.Markdown("## WordPress site")
                website_name = gr.Textbox(
                    label="Website Name",
                    lines=1,
                    info="Example: My WP Blog",
                    interactive=True,
                )
                domain_name = gr.Textbox(
                    label="Fully Qualified Domain Name",
                    lines=1,
                    info="Example: mywpblog.com",
                    interactive=True,
                )
                enable_logging = gr.Checkbox(
                    label="Enable Logging",
                    info="Enables activity logging in workflows",
                    interactive=True,
                )
                status_dropdown = gr.Dropdown(
                    label="Default Status",
                    choices=["Draft", "Publish"],
                    info="Set default posting status.",
                    interactive=True,
                )
                gr.Markdown("## Social Posting")
                x_posting = gr.Checkbox(
                    label="X Social Posting",
                    info="Enable X (formerly Twitter) integration",
                    interactive=True,
                )

                x_posting_auto = gr.Checkbox(
                    label="X Auto Posting",
                    info="Enable automatic X (formerly Twitter) posting",
                    interactive=True,
                )
                telegram_sharing = gr.Checkbox(
                    label="Telegram Sharing",
                    info="Enable Telegram integration",
                    interactive=True,
                )
                telegram_sharing_auto = gr.Checkbox(
                    label="Telegram Auto Sharing",
                    info="Enable automatic Telegram sharing",
                    interactive=True,
                )
                social_sharing_override = gr.Checkbox(
                    label="Override Social Sharing Configuration",
                    info="Enable or disable social sharing for all workflows. If you want to have fine-grained control over social sharing per workflow, leave this unchecked.",
                    interactive=True,
                )
                gr.Markdown("## Image Optimization")
                image_seo = gr.Checkbox(
                    label="Image SEO Attributes",
                    info="Enable image SEO attribute generation",
                    interactive=True,
                )
                picture_format = gr.Textbox(
                    label="Picture Format",
                    info="Preferred image format for your posts",
                    lines=1,
                    interactive=True,
                )
                enable_imagick = gr.Checkbox(
                    label="Enable ImageMagick",
                    info="Use ImageMagick for image processing",
                    interactive=True,
                )
                img_quality = gr.Slider(
                    0,
                    100,
                    label="Image Quality",
                    info="Choose your image compression quality",
                    interactive=True,
                )

                fallback_img_format = gr.Textbox(
                    label="Fallback Picture Format",
                    info="Source format of your post images",
                    lines=1,
                    interactive=True,
                )
                gr.Markdown("## Large Language Model (LLM) Integration")
                llm_providers = gr.Radio(
                    label="LLM Providers",
                    choices=["Ollama", "LMStudio"],
                )
                llm_tag = gr.Textbox(
                    label="Model Tag",
                    info="Provide the tag of the model you will be using",
                    interactive=True,
                )
                llm_host = gr.Textbox(
                    label="Provider Host",
                    info="LLM provider hostname/address",
                    interactive=True,
                )
                llm_port = gr.Number(
                    label="Provider Port",
                    info="LLM provider port number",
                    interactive=True,
                )

            with gr.Tab("Content Providers"):
                gr.Markdown("## FeedAlpha")
                feed_alpha_campaign_id = gr.Number(
                    label="FeedAlpha Campaign ID",
                    info="Campaign ID from the FeedAlpha feeds",
                )

                gr.Markdown("## FeedBeta")
                feed_beta_source_id = gr.Number(
                    label="FeedBeta Source ID",
                    info="ID identifier of your traffic source",
                )

                gr.Markdown("## FeedDelta")
                feed_delta_campaign_utm = gr.Textbox(
                    label="FeedDelta Campaign UTM",
                    info='Found in the data feed as "utm_campaign=xx.xxx"',
                )

            with gr.Tab("Workflows"):
                gr.Markdown("## Video Embed Assistant")
                embed_sql_query = gr.Textbox(
                    label="Database Query",
                    info="Use this query to filter your content or select relevant attributes",
                )
                embed_x_posting = gr.Checkbox(
                    label="X Posting Support",
                    info="Enable X (formerly Twitter) integration. Make sure your integration is set up.",
                )
                embed_x_posting_auto = gr.Checkbox(
                    label="X Posting Auto",
                    info="Enable this if you want to automatically post content to X.",
                )
                embed_telegram_sharing = gr.Checkbox(
                    label="Telegram Sharing",
                    info="Enable Telegram integration. Make sure your integration is set up.",
                )
                embed_telegram_sharing_auto = gr.Checkbox(
                    label="Telegram Sharing Auto",
                    info="Enable this if you want to automatically share content to Telegram.",
                )
                embed_partner = gr.Textbox(
                    label="Partner(s)",
                    info="The name of your partner or comma separated list of partners.",
                )

                gr.Markdown("## MediaSource Content Bots")
                gr.Markdown("### Content Bot")
                content_bot_sql_query = gr.Textbox(
                    label="Database Query",
                    info="Use this query to filter your content or select relevant attributes",
                )
                content_bot_x_posting = gr.Checkbox(
                    label="X Posting Support",
                    info="Enable X (formerly Twitter) integration. Make sure your integration is set up.",
                )
                content_bot_x_posting_auto = gr.Checkbox(
                    label="X Posting Auto",
                    info="Enable this if you want to automatically post content to X.",
                )
                content_bot_telegram_sharing = gr.Checkbox(
                    label="Telegram Sharing",
                    info="Enable Telegram integration. Make sure your integration is set up.",
                )
                content_bot_telegram_sharing_auto = gr.Checkbox(
                    label="Telegram Sharing Auto",
                    info="Enable this if you want to automatically share content to Telegram.",
                )
                content_bot_partner = gr.Textbox(
                    label="Partner(s)",
                    info="The name of your partner or comma separated list of partners.",
                )
                content_bot_enable_assets = gr.Checkbox(
                    label="Enable Assets",
                    info="If you enable this option, you need to provide the assets configuration. Refer to the documentation for more details",
                    interactive=True,
                )
                content_bot_assets = gr.Textbox(
                    label="Assets file",
                    info="The assets configuration for your content bot. Refer to the documentation for more details.",
                    interactive=True,
                )

                gr.Markdown("### Image Gallery Bot")
                media_source_image_gallery_bot_sql_query = gr.Textbox(
                    label="Database Query",
                    info="Use this query to filter your content or select relevant attributes",
                )
                media_source_image_gallery_bot_x_posting = gr.Checkbox(
                    label="X Posting Support",
                    info="Enable X (formerly Twitter) integration. Make sure your integration is set up.",
                )
                media_source_image_gallery_bot_x_posting_auto = gr.Checkbox(
                    label="X Posting Auto",
                    info="Enable this if you want to automatically post content to X.",
                )
                media_source_image_gallery_bot_telegram_sharing = gr.Checkbox(
                    label="Telegram Sharing",
                    info="Enable Telegram integration. Make sure your integration is set up.",
                )
                media_source_image_gallery_bot_telegram_sharing_auto = gr.Checkbox(
                    label="Telegram Sharing Auto",
                    info="Enable this if you want to automatically share content to Telegram.",
                )
                media_source_image_gallery_bot_partner = gr.Textbox(
                    label="Partner(s)",
                    info="The name of your partner or comma separated list of partners.",
                )

            gr.Markdown("## Save Config")
            save_button = gr.Button(value="Save config")
            repair_button = gr.Button(value="Repair config file")

            config_values = [
                website_name,
                domain_name,
                enable_logging,
                status_dropdown,
                x_posting,
                x_posting_auto,
                telegram_sharing,
                telegram_sharing_auto,
                social_sharing_override,
                image_seo,
                picture_format,
                enable_imagick,
                img_quality,
                fallback_img_format,
                llm_providers,
                llm_tag,
                llm_host,
                llm_port,
                feed_alpha_campaign_id,
                feed_beta_source_id,
                feed_delta_campaign_utm,
                embed_sql_query,
                embed_x_posting,
                embed_x_posting_auto,
                embed_telegram_sharing,
                embed_telegram_sharing_auto,
                embed_partner,
                content_bot_sql_query,
                content_bot_x_posting,
                content_bot_x_posting_auto,
                content_bot_telegram_sharing,
                content_bot_telegram_sharing_auto,
                content_bot_partner,
                content_bot_enable_assets,
                content_bot_assets,
                media_source_image_gallery_bot_sql_query,
                media_source_image_gallery_bot_x_posting,
                media_source_image_gallery_bot_x_posting_auto,
                media_source_image_gallery_bot_telegram_sharing,
                media_source_image_gallery_bot_telegram_sharing_auto,
                media_source_image_gallery_bot_partner,
            ]

            save_button.click(
                fn=collect_config_state,
                inputs=config_values,
                outputs=[],
                trigger_mode="multiple",
            )

            repair_button.click(
                fn=repair_from_template, inputs=[], outputs=[], trigger_mode="once"
            )
            conf_mgr.load(fn=load_config_fields, outputs=config_values)


if __name__ == "__main__":
    try:
        # Environment variable set in the ``logging_setup()`` function in the helpers.py file.
        logging_path = os.path.join(Path(__file__).parent.parent, "logs")
        logging_setup(logging_path, __file__)
        print("Starting Workflow Tweaks...")
        print(f"Logging path at: {os.path.abspath(logging_path)}")
        conf_mgr.launch(server_port=9080, show_api=False)
    finally:
        logging.shutdown()

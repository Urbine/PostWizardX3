"""
PostWizard - Workflow Tweaks View

This module defines the Gradio interface for managing workflow tweaks.
It allows users to set up various tweaks and configurations for workflows present in PostWizard.

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
from core.utils.file_system import logging_setup

with gr.Blocks(theme=elegant_theme, title="PostWizard - Workflow Tweaks") as conf_mgr:
    gr.Markdown("# PostWizard - Workflow Settings")
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
                gr.Markdown("## AdultNext")
                anxt_campaign_id = gr.Number(
                    label="AdultNext Campaign ID",
                    info="Campaign ID from the AdultNext feeds",
                )

                gr.Markdown("## TubeCorporate")
                tubecorp_source_id = gr.Number(
                    label="TubeCorporate Source ID",
                    info="ID identifier of your traffic source",
                )

                gr.Markdown("## FapHouse")
                fp_house_campaign_utm = gr.Textbox(
                    label="FapHouse Campaign UTM",
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

                gr.Markdown("## MongerCash Content Bots")
                gr.Markdown("### Content Bot")
                mcash_content_bot_sql_query = gr.Textbox(
                    label="Database Query",
                    info="Use this query to filter your content or select relevant attributes",
                )
                mcash_content_bot_x_posting = gr.Checkbox(
                    label="X Posting Support",
                    info="Enable X (formerly Twitter) integration. Make sure your integration is set up.",
                )
                mcash_content_bot_x_posting_auto = gr.Checkbox(
                    label="X Posting Auto",
                    info="Enable this if you want to automatically post content to X.",
                )
                mcash_content_bot_telegram_sharing = gr.Checkbox(
                    label="Telegram Sharing",
                    info="Enable Telegram integration. Make sure your integration is set up.",
                )
                mcash_content_bot_telegram_sharing_auto = gr.Checkbox(
                    label="Telegram Sharing Auto",
                    info="Enable this if you want to automatically share content to Telegram.",
                )
                mcash_content_bot_partner = gr.Textbox(
                    label="Partner(s)",
                    info="The name of your partner or comma separated list of partners.",
                )
                mcash_content_bot_enable_assets = gr.Checkbox(
                    label="Enable Assets",
                    info="If you enable this option, you need to provide the assets configuration. Refer to the documentation for more details",
                    interactive=True,
                )
                mcash_content_bot_assets = gr.Textbox(
                    label="Assets file",
                    info="The assets configuration for your content bot. Refer to the documentation for more details.",
                    interactive=True,
                )

                gr.Markdown("### Image Gallery Bot")
                mcash_image_gallery_bot_sql_query = gr.Textbox(
                    label="Database Query",
                    info="Use this query to filter your content or select relevant attributes",
                )
                mcash_image_gallery_bot_x_posting = gr.Checkbox(
                    label="X Posting Support",
                    info="Enable X (formerly Twitter) integration. Make sure your integration is set up.",
                )
                mcash_image_gallery_bot_x_posting_auto = gr.Checkbox(
                    label="X Posting Auto",
                    info="Enable this if you want to automatically post content to X.",
                )
                mcash_image_gallery_bot_telegram_sharing = gr.Checkbox(
                    label="Telegram Sharing",
                    info="Enable Telegram integration. Make sure your integration is set up.",
                )
                mcash_image_gallery_bot_telegram_sharing_auto = gr.Checkbox(
                    label="Telegram Sharing Auto",
                    info="Enable this if you want to automatically share content to Telegram.",
                )
                mcash_image_gallery_bot_partner = gr.Textbox(
                    label="Partner(s)",
                    info="The name of your partner or comma separated list of partners.",
                )
            with gr.Tab("PostWizard API"):
                pw_api_base = gr.Textbox(
                    label="PostWizard API Base URL",
                    info="Base URL of your PostWizard Server instance",
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
                anxt_campaign_id,
                tubecorp_source_id,
                fp_house_campaign_utm,
                embed_sql_query,
                embed_x_posting,
                embed_x_posting_auto,
                embed_telegram_sharing,
                embed_telegram_sharing_auto,
                embed_partner,
                mcash_content_bot_sql_query,
                mcash_content_bot_x_posting,
                mcash_content_bot_x_posting_auto,
                mcash_content_bot_telegram_sharing,
                mcash_content_bot_telegram_sharing_auto,
                mcash_content_bot_partner,
                mcash_content_bot_enable_assets,
                mcash_content_bot_assets,
                mcash_image_gallery_bot_sql_query,
                mcash_image_gallery_bot_x_posting,
                mcash_image_gallery_bot_x_posting_auto,
                mcash_image_gallery_bot_telegram_sharing,
                mcash_image_gallery_bot_telegram_sharing_auto,
                mcash_image_gallery_bot_partner,
                pw_api_base,
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

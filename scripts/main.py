import gradio as gr

from modules import script_callbacks, shared
from modules.call_queue import wrap_gradio_gpu_call
from modules.shared import cmd_opts
from modules.ui import setup_progressbar


def on_ui_tabs():
    with gr.Blocks() as template_interface:
        with gr.Row(equal_height=True):
            with gr.Column(variant="panel"):
                with gr.Tab("Tab 1"):
                    sp_src = gr.Textbox(label='Source directory')
                    sp_dst = gr.Textbox(label='Destination directory')

                with gr.Tab("Tab 2"):
                    sp_size = gr.Slider(minimum=64, maximum=2048, step=64, label="Output Size", value=512)
                    sp_pad = gr.Checkbox(label="Pad Images")
                    sp_crop = gr.Checkbox(label='Crop Images')
                    sp_flip = gr.Checkbox(label='Create flipped copies')

                with gr.Tab("Tab 3"):
                    sp_caption = gr.Checkbox(label='Generate Captions')
                    sp_caption_length = gr.Slider(label='Max Caption Length (0=unlimited)', value=75, step=75, minimum=0, maximum=150)
                    sp_txt_action = gr.Dropdown(label='Existing Caption Action', value="ignore",
                                                choices=["ignore", "copy", "prepend", "append"])
                    sp_caption_clip = gr.Checkbox(label="Add CLIP results to Caption")
                    sp_num_beams = gr.Slider(label="Number of CLIP beams", value=8, minimum=1, maximum=20)
                    sp_min_clip = gr.Slider(label="CLIP Minimum length", value=30, minimum=5, maximum=75, step=1)
                    sp_max_clip = gr.Slider(label="CLIP Maximum length", value=50, minimum=5, maximum=75, step=1)
                    sp_clip_use_v2 = gr.Checkbox(label="Use v2 CLIP Model", value=True)
                    sp_clip_append_flavor = gr.Checkbox(label="Append Flavor tags from CLIP")
                    sp_clip_max_flavors = gr.Number(label="Max flavors to append.", value=4, precision=0)
                    sp_clip_append_medium = gr.Checkbox(label="Append Medium tags from CLIP")
                    sp_clip_append_movement = gr.Checkbox(label="Append Movement tags from CLIP")
                    sp_clip_append_artist = gr.Checkbox(label="Append Artist tags from CLIP")
                    sp_clip_append_trending = gr.Checkbox(label="Append Trending tags from CLIP")
                    sp_caption_wd14 = gr.Checkbox(label="Add WD14 Tags to Caption")
                    sp_wd14_min_score = gr.Slider(label="Minimum Score for WD14 Tags", value=0.85, minimum=0.01,
                                                  maximum=1,
                                                  step=0.01)
                    sp_caption_deepbooru = gr.Checkbox(label='Add DeepDanbooru Tags to Caption',
                                                       visible=True if cmd_opts.deepdanbooru else False)
                    sp_booru_min_score = gr.Slider(label="Minimum Score for DeepDanbooru Tags", value=0.85,
                                                   minimum=0.01, maximum=1, step=0.01)
                    sp_tags_to_ignore = gr.Textbox(label="Tags To Ignore", value="")
                    sp_replace_class = gr.Checkbox(label='Replace Class with Subject in Caption', value=False)
                    sp_class = gr.Textbox(label='Subject Class', placeholder='Subject class to crop (leave '
                                                                             'blank to auto-detect)')
                    sp_subject = gr.Textbox(label='Subject Name', placeholder='Subject Name to replace class '
                                                                              'with in captions')

                with gr.Tab("Tab 4"):
                    sp_restore_faces = gr.Checkbox(label='Restore Faces', value=False)
                    sp_face_model = gr.Dropdown(label="Face Restore Model", choices=["GFPGAN", "Codeformer"],
                                                value="GFPGAN")
                    sp_upscale = gr.Checkbox(label='Upscale and Resize', value=False)
                    sp_upscale_ratio = gr.Slider(label="Upscale Ratio", value=2, step=1, minimum=2, maximum=4)
                    sp_scaler = gr.Radio(label='Upscaler', elem_id="sp_scaler",
                                         choices=[x.name for x in shared.sd_upscalers],
                                         value=shared.sd_upscalers[0].name, type="index")
                    
                with gr.Tab("Tab 5"):
                    ffmpeg_mode = gr.Dropdown(label="Process Mode", choices=["Video to Sequence", "Sequence to Video"],value='Video to Sequence',interactive=True)
                    ffmpeg_seq_intput = gr.Textbox(label='Sequence Folder Input', visible=False, interactive=True)
                    ffmpeg_movie_intput = gr.File(label='Movie File Input', visible=True, interactive=True)
                    ffmpeg_seq_output = gr.Textbox(label='Sequence Folder Output', visible=True, interactive=True)
                    ffmpeg_movie_output = gr.Textbox(label='Movie File Output', visible=False, interactive=True)
                        
                    
                def update_ffmpeg_ui(mode):
                    if mode == 'Video to Sequence':
                        ui_status = {ffmpeg_seq_intput: gr.update(visible=False),
                                  ffmpeg_movie_intput: gr.update(visible=True), 
                                  ffmpeg_seq_output: gr.update(visible=True), 
                                  ffmpeg_movie_output: gr.update(visible=False)}
                    elif mode == 'Sequence to Video':
                        ui_status = {ffmpeg_seq_intput: gr.update(visible=True),
                                  ffmpeg_movie_intput: gr.update(visible=False), 
                                  ffmpeg_seq_output: gr.update(visible=False), 
                                  ffmpeg_movie_output: gr.update(visible=True)}
                    return ui_status
                ffmpeg_mode.change(
                    fn=update_ffmpeg_ui,
                    inputs=[ffmpeg_mode],
                    outputs=[ffmpeg_seq_intput, ffmpeg_seq_output,ffmpeg_movie_intput,ffmpeg_movie_output],
        )
                    
            # Preview/progress
            with gr.Column(variant="panel"):
                sp_progress = gr.HTML(elem_id="sp_progress", value="")
                sp_outcome = gr.HTML(elem_id="sp_error", value="")
                sp_progressbar = gr.HTML(elem_id="sp_progressbar")
                sp_gallery = gr.Gallery(label='Output', show_label=False, elem_id='sp_gallery').style(grid=4)
                sp_preview = gr.Image(elem_id='sp_preview', visible=False)
                setup_progressbar(sp_progressbar, sp_preview, 'sp', textinfo=sp_progress)

        with gr.Row():
            sp_cancel = gr.Button(value="Cancel")
            sp_run = gr.Button(value="Preprocess", variant='primary')



        sp_cancel.click(
            fn=lambda: shared.state.interrupt()
        )


    return (template_interface, "Example Tab", "example_interface"),


script_callbacks.on_ui_tabs(on_ui_tabs)

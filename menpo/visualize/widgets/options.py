from IPython.html.widgets import (FloatSliderWidget, ContainerWidget,
                                  IntSliderWidget, CheckboxWidget,
                                  ToggleButtonWidget, RadioButtonsWidget,
                                  IntTextWidget, DropdownWidget, LatexWidget,
                                  ButtonWidget, SelectWidget, FloatTextWidget,
                                  TextWidget, TabWidget, ImageWidget,
                                  BoundedIntTextWidget)
import numpy as np
from collections import OrderedDict
from functools import partial

from .tools import (colour_selection, format_colour_selection,
                    hog_options, format_hog_options, igo_options,
                    format_igo_options, lbp_options,
                    format_lbp_options, daisy_options,
                    format_daisy_options, _convert_image_to_bytes,
                    line_options, format_line_options,
                    update_line_options, marker_options,
                    format_marker_options, update_marker_options,
                    numbering_options, format_numbering_options,
                    update_numbering_options, figure_options,
                    format_figure_options, update_figure_options,
                    figure_options_two_scales,
                    format_figure_options_two_scales,
                    update_figure_options_two_scales,
                    index_selection_slider, index_selection_buttons,
                    format_index_selection, update_index_selection,
                    legend_options, format_legend_options,
                    update_legend_options)


def channel_options(channels_options_default, plot_function=None,
                    toggle_show_default=True, toggle_show_visible=True):
    r"""
    Creates a widget with Channel Options. Specifically, it has:
        1) Two radio buttons that select an options mode, depending on whether
           the user wants to visualize a "Single" or "Multiple" channels.
        2) If mode is "Single", the channel number is selected by one slider.
           If mode is "Multiple", the channel range is selected by two sliders.
        3) If mode is "Single" and the image has 3 channels, there is a checkbox
           option to visualize the image in RGB mode.
        4) If mode is "Multiple", there is a checkbox option to visualize the
           sum of the channels.
        5) If mode is "Multiple", there is a checkbox option to visualize the
           glyph.
        6) The glyph option is accompanied by a block size text field and a
           checkbox that enables negative values visualization.
        7) A checkbox that defines whether the masked image will be displayed.
        8) A toggle button that controls the visibility of all the above, i.e.
           the channel options.

    The structure of the widgets is the following:
        channel_options_wid.children = [toggle_button, all_but_toggle]
        all_but_toggle.children = [mode_and_masked, all_but_radio_buttons]
        mode_and_masked.children = [mode_radio_buttons, masked_checkbox]
        all_but_radio_buttons.children = [all_sliders, multiple_checkboxes]
        all_sliders.children = [first_slider, second_slider]
        multiple_checkboxes.children = [sum_checkbox, glyph_all, rgb_checkbox]
        glyph_all.children = [glyph_checkbox, glyph_options]
        glyph_options.children = [block_size_text, use_negative_checkbox]

    The returned widget saves the selected values in the following dictionary:
        channel_options_wid.selected_values

    To fix the alignment within this widget please refer to
    `format_channel_options()` function.

    To update the state of this widget, please refer to
    `update_channel_options()` function.

    Parameters
    ----------
    channels_options_default : `dict`
        The initial options. For example:
            channels_options_default = {'n_channels': 10,
                                        'image_is_masked': True,
                                        'channels': 0,
                                        'glyph_enabled': False,
                                        'glyph_block_size': 3,
                                        'glyph_use_negative': False,
                                        'sum_enabled': False,
                                        'masked_enabled': True}

    plot_function : `function` or None, optional
        The plot function that is executed when a widgets' value changes.
        If None, then nothing is assigned.

    toggle_show_default : `boolean`, optional
        Defines whether the options will be visible upon construction.

    toggle_show_visible : `boolean`, optional
        The visibility of the toggle button.
    """
    # if image is not masked, then masked flag should be disabled
    if not channels_options_default['image_is_masked']:
        channels_options_default['masked_enabled'] = False

    # parse channels
    if isinstance(channels_options_default['channels'], list):
        if len(channels_options_default['channels']) == 1:
            mode_default = 'Single'
            first_slider_default = channels_options_default['channels'][0]
            second_slider_default = channels_options_default['n_channels']-1
        else:
            mode_default = 'Multiple'
            first_slider_default = min(channels_options_default['channels'])
            second_slider_default = max(channels_options_default['channels'])
    elif channels_options_default['channels'] is None:
        mode_default = 'Single'
        first_slider_default = 0
        second_slider_default = channels_options_default['n_channels']-1
    else:
        mode_default = 'Single'
        first_slider_default = channels_options_default['channels']
        second_slider_default = channels_options_default['n_channels']-1

    # Create all necessary widgets
    # If single channel, disable all options apart from masked
    but = ToggleButtonWidget(description='Channels Options',
                             value=toggle_show_default,
                             visible=toggle_show_visible)
    mode = RadioButtonsWidget(
        values=["Single", "Multiple"], value=mode_default, description='Mode:',
        visible=toggle_show_default,
        disabled=channels_options_default['n_channels'] == 1)
    masked = CheckboxWidget(
        value=channels_options_default['masked_enabled'], description='Masked',
        visible=toggle_show_default and channels_options_default['image_is_masked'])
    first_slider_wid = IntSliderWidget(
        min=0, max=channels_options_default['n_channels']-1, step=1,
        value=first_slider_default, description='Channel',
        visible=toggle_show_default,
        disabled=channels_options_default['n_channels'] == 1)
    second_slider_wid = IntSliderWidget(
        min=1, max=channels_options_default['n_channels']-1, step=1,
        value=second_slider_default, description='To',
        visible=mode_default == "Multiple",
        disabled=channels_options_default['n_channels'] == 1)
    rgb_wid = CheckboxWidget(
        value=channels_options_default['n_channels'] == 3 and channels_options_default['channels'] == None,
        description='RGB',
        visible=toggle_show_default and channels_options_default['n_channels'] == 3)
    sum_wid = CheckboxWidget(
        value=channels_options_default['sum_enabled'], description='Sum',
        visible=False, disabled=channels_options_default['n_channels'] == 1)
    glyph_wid = CheckboxWidget(
        value=channels_options_default['glyph_enabled'], description='Glyph',
        visible=False, disabled=channels_options_default['n_channels'] == 1)
    glyph_block_size = BoundedIntTextWidget(
        description='Block size', min=1, max=25,
        value=channels_options_default['glyph_block_size'], visible=False,
        disabled=channels_options_default['n_channels'] == 1)
    glyph_use_negative = CheckboxWidget(
        description='Negative values',
        value=channels_options_default['glyph_use_negative'], visible=False,
        disabled=channels_options_default['n_channels'] == 1)

    # Group widgets
    glyph_options = ContainerWidget(children=[glyph_block_size,
                                              glyph_use_negative])
    glyph_all = ContainerWidget(children=[glyph_wid, glyph_options])
    multiple_checkboxes = ContainerWidget(children=[sum_wid, glyph_all,
                                                    rgb_wid])
    sliders = ContainerWidget(children=[first_slider_wid, second_slider_wid])
    all_but_radiobuttons = ContainerWidget(children=[sliders,
                                                     multiple_checkboxes])
    mode_and_masked = ContainerWidget(children=[mode, masked])
    all_but_toggle = ContainerWidget(children=[mode_and_masked,
                                               all_but_radiobuttons])

    # Widget container
    channel_options_wid = ContainerWidget(children=[but, all_but_toggle])

    # Initialize output variables
    channel_options_wid.selected_values = channels_options_default

    # Define mode visibility
    def mode_selection_fun(name, value):
        if value == 'Single':
            first_slider_wid.description = 'Channel'
            first_slider_wid.min = 0
            first_slider_wid.max = \
                channel_options_wid.selected_values['n_channels'] - 1
            second_slider_wid.visible = False
            sum_wid.visible = False
            sum_wid.value = False
            glyph_wid.visible = False
            glyph_wid.value = False
            glyph_block_size.visible = False
            glyph_block_size.value = '3'
            glyph_use_negative.visible = False
            glyph_use_negative.value = False
            rgb_wid.visible = \
                channel_options_wid.selected_values['n_channels'] == 3
            rgb_wid.value = \
                channel_options_wid.selected_values['n_channels'] == 3
        else:
            first_slider_wid.description = 'From'
            first_slider_wid.min = 0
            first_slider_wid.max = \
                channel_options_wid.selected_values['n_channels'] - 1
            second_slider_wid.min = 0
            second_slider_wid.max = \
                channel_options_wid.selected_values['n_channels'] - 1
            second_slider_wid.value = first_slider_wid.value
            second_slider_wid.visible = True
            rgb_wid.visible = False
            rgb_wid.value = False
            sum_wid.visible = True
            sum_wid.value = False
            glyph_wid.visible = True
            glyph_wid.value = False
            glyph_block_size.visible = False
            glyph_block_size.value = '3'
            glyph_use_negative.visible = False
            glyph_use_negative.value = False
    mode_selection_fun('', mode_default)
    second_slider_wid.value - second_slider_default
    mode.on_trait_change(mode_selection_fun, 'value')

    # Define glyph visibility
    def glyph_options_visibility_fun(name, value):
        glyph_block_size.visible = glyph_wid.value
        glyph_use_negative.visible = glyph_wid.value
        if glyph_wid.value:
            sum_wid.value = False
    glyph_wid.on_trait_change(glyph_options_visibility_fun, 'value')
    glyph_wid.on_trait_change(glyph_options_visibility_fun, 'visible')

    # Define rgb functionality
    def rgb_fun(name, value):
        first_slider_wid.disabled = value
    rgb_wid.on_trait_change(rgb_fun, 'value')

    # Define sum functionality
    def sum_fun(name, value):
        if value:
            glyph_wid.value = False
    sum_wid.on_trait_change(sum_fun, 'value')

    # Define masked functionality
    def masked_fun(name, value):
        channel_options_wid.masked_enabled = value
    masked.on_trait_change(masked_fun, 'value')

    # Function that gets glyph/sum options
    def get_glyph_options(name, value):
        channel_options_wid.selected_values['glyph_enabled'] = glyph_wid.value
        channel_options_wid.selected_values['sum_enabled'] = sum_wid.value
        channel_options_wid.selected_values['glyph_use_negative'] = glyph_use_negative.value
        channel_options_wid.selected_values['glyph_block_size'] = glyph_block_size.value
        if channel_options_wid.selected_values['sum_enabled']:
            channel_options_wid.selected_values['glyph_block_size'] = 1
    glyph_wid.on_trait_change(get_glyph_options, 'value')
    sum_wid.on_trait_change(get_glyph_options, 'value')
    glyph_use_negative.on_trait_change(get_glyph_options, 'value')
    glyph_block_size.on_trait_change(get_glyph_options, 'value')
    mode.on_trait_change(get_glyph_options, 'value')

    # Define multiple channels sliders functionality
    def first_slider_val(name, value):
        if mode.value == 'Multiple' and value > second_slider_wid.value:
            first_slider_wid.value = second_slider_wid.value

    def second_slider_val(name, value):
        if mode.value == 'Multiple' and value < first_slider_wid.value:
            second_slider_wid.value = first_slider_wid.value

    def get_channels(name, value):
        if mode.value == "Single":
            if rgb_wid.value:
                channel_options_wid.selected_values['channels'] = None
            else:
                channel_options_wid.selected_values['channels'] = first_slider_wid.value
        else:
            channel_options_wid.selected_values['channels'] = range(first_slider_wid.value,
                                                 second_slider_wid.value + 1)
    first_slider_wid.on_trait_change(first_slider_val, 'value')
    second_slider_wid.on_trait_change(second_slider_val, 'value')
    first_slider_wid.on_trait_change(get_channels, 'value')
    second_slider_wid.on_trait_change(get_channels, 'value')
    rgb_wid.on_trait_change(get_channels, 'value')
    mode.on_trait_change(get_channels, 'value')

    def get_masked(name, value):
        channel_options_wid.selected_values['masked_enabled'] = value
    masked.on_trait_change(get_masked, 'value')

    # Toggle button function
    def toggle_image_options(name, value):
        mode.visible = value
        if value:
            masked.visible = channel_options_wid.selected_values['image_is_masked']
            if mode.value == 'Single':
                first_slider_wid.visible = True
                rgb_wid.visible = channel_options_wid.selected_values['n_channels'] == 3
            else:
                first_slider_wid.visible = True
                second_slider_wid.visible = True
                sum_wid.visible = True
                glyph_wid.visible = True
        else:
            masked.visible = False
            first_slider_wid.visible = False
            second_slider_wid.visible = False
            rgb_wid.visible = False
            sum_wid.visible = False
            glyph_wid.visible = False
            glyph_options.children[0].visible = False
            glyph_options.children[1].visible = False
    but.on_trait_change(toggle_image_options, 'value')

    # assign plot_function
    if plot_function is not None:
        #mode.on_trait_change(plot_function, 'value')
        masked.on_trait_change(plot_function, 'value')
        first_slider_wid.on_trait_change(plot_function, 'value')
        second_slider_wid.on_trait_change(plot_function, 'value')
        rgb_wid.on_trait_change(plot_function, 'value')
        sum_wid.on_trait_change(plot_function, 'value')
        glyph_wid.on_trait_change(plot_function, 'value')
        glyph_block_size.on_trait_change(plot_function, 'value')
        glyph_use_negative.on_trait_change(plot_function, 'value')

    return channel_options_wid


def format_channel_options(channel_options_wid, container_padding='6px',
                           container_margin='6px',
                           container_border='1px solid black',
                           toggle_button_font_weight='bold',
                           border_visible=True):
    r"""
    Function that corrects the align (style format) of a given channel_options
    widget. Usage example:
        channel_options_wid = channel_options()
        display(channel_options_wid)
        format_channel_options(channel_options_wid)

    Parameters
    ----------
    channel_options_wid :
        The widget object generated by the `channel_options()` function.

    container_padding : `str`, optional
        The padding around the widget, e.g. '6px'

    container_margin : `str`, optional
        The margin around the widget, e.g. '6px'

    container_border : `str`, optional
        The border around the widget, e.g. '1px solid black'

    toggle_button_font_weight : `str`
        The font weight of the toggle button, e.g. 'bold'

    border_visible : `boolean`, optional
        Defines whether to draw the border line around the widget.
    """
    # align glyph options
    channel_options_wid.children[1].children[1].children[1].children[1].children[1].remove_class('vbox')
    channel_options_wid.children[1].children[1].children[1].children[1].children[1].add_class('hbox')
    channel_options_wid.children[1].children[1].children[1].children[1].children[1].children[0].set_css('width', '0.8cm')

    # align sum and glyph checkboxes
    channel_options_wid.children[1].children[1].children[1].remove_class('vbox')
    channel_options_wid.children[1].children[1].children[1].add_class('hbox')

    # align radio buttons with the rest
    channel_options_wid.children[1].remove_class('vbox')
    channel_options_wid.children[1].add_class('hbox')
    channel_options_wid.children[1].add_class('align-start')

    # set toggle button font bold
    channel_options_wid.children[0].set_css('font-weight',
                                            toggle_button_font_weight)

    # margin and border around container widget
    channel_options_wid.set_css('padding', container_padding)
    channel_options_wid.set_css('margin', container_margin)
    if border_visible:
        channel_options_wid.set_css('border', container_border)


def update_channel_options(channel_options_wid, n_channels, image_is_masked,
                           masked_default=False):
    r"""
    Function that updates the state of a given channel_options widget if the
    image's number of channels or its masked flag has changed. Usage example:
        channel_options_wid = channel_options(n_channels=2, image_is_masked=True)
        display(channel_options_wid)
        format_channel_options(channel_options_wid)
        update_channel_options(channel_options_wid, n_channels=36,
                               image_is_masked=False)

    Parameters
    ----------
    channel_options_wid :
        The widget object generated by the `channel_options()` function.

    n_channels : `int`
        The number of channels.

    image_is_masked : `boolean`
        Flag that defines whether the image is an instance of :map:`MaskedImage` or subclass.

    masked_default : `boolean`, optional
        The value to be assigned at the masked checkbox.
    """
    # if image_is_masked flag has actually changed from the previous value
    if image_is_masked != channel_options_wid.selected_values['image_is_masked']:
        # change the channel_options output
        channel_options_wid.selected_values['image_is_masked'] = image_is_masked
        channel_options_wid.selected_values['masked_enabled'] = masked_default
        # set the masked checkbox state
        channel_options_wid.children[1].children[0].children[1].visible = \
            channel_options_wid.children[0].value and image_is_masked
        channel_options_wid.children[1].children[0].children[1].value = False

    # if n_channels are actually different from the previous value
    if n_channels != channel_options_wid.selected_values['n_channels']:
        # change the channel_options output
        channel_options_wid.selected_values['n_channels'] = n_channels
        channel_options_wid.selected_values['channels'] = 0
        # set the rgb checkbox state
        channel_options_wid.children[1].children[1].children[1].children[2].visible = \
            n_channels == 3 and channel_options_wid.children[0].value
        # set the channel options state (apart from the masked checkbox)
        if n_channels == 1:
            # set sliders max and min values
            channel_options_wid.children[1].children[1].children[0].children[0].max = 1
            channel_options_wid.children[1].children[1].children[0].children[1].max = 1
            channel_options_wid.children[1].children[1].children[0].children[0].min = 0
            channel_options_wid.children[1].children[1].children[0].children[1].min = 0
            # set sliders state
            channel_options_wid.children[1].children[1].children[0].children[0].disabled = True
            channel_options_wid.children[1].children[1].children[0].children[1].visible = False
            # set glyph/sum state
            channel_options_wid.children[1].children[1].children[1].children[0].disabled = True
            channel_options_wid.children[1].children[1].children[1].children[1].children[0].disabled = True
            channel_options_wid.children[1].children[1].children[1].children[1].children[1].children[0].disabled = True
            channel_options_wid.children[1].children[1].children[1].children[1].children[1].children[1].disabled = True
            # set mode state
            channel_options_wid.children[1].children[0].children[0].disabled = True
            # set mode and sliders values
            for k in range(4):
                if k == 0:
                    channel_options_wid.children[1].children[1].children[1].children[2].value = False
                elif k == 1:
                    channel_options_wid.children[1].children[0].children[0].value = "Single"
                elif k == 2:
                    channel_options_wid.children[1].children[1].children[0].children[0].value = 0
                else:
                    channel_options_wid.children[1].children[1].children[0].children[1].value = 0
        else:
            # set sliders max and min values
            channel_options_wid.children[1].children[1].children[0].children[0].max = n_channels - 1
            channel_options_wid.children[1].children[1].children[0].children[1].max = n_channels - 1
            channel_options_wid.children[1].children[1].children[0].children[0].min = 0
            channel_options_wid.children[1].children[1].children[0].children[1].min = 0
            # set sliders state
            channel_options_wid.children[1].children[1].children[0].children[0].disabled = False
            channel_options_wid.children[1].children[1].children[0].children[1].visible = False
            # set glyph/sum state
            channel_options_wid.children[1].children[1].children[1].children[0].disabled = False
            channel_options_wid.children[1].children[1].children[1].children[1].children[0].disabled = False
            channel_options_wid.children[1].children[1].children[1].children[1].children[1].children[0].disabled = False
            channel_options_wid.children[1].children[1].children[1].children[1].children[1].children[1].disabled = False
            # set mode state
            channel_options_wid.children[1].children[0].children[0].disabled = False
            # set mode and sliders values
            for k in range(4):
                if k == 0:
                    channel_options_wid.children[1].children[1].children[1].children[2].value = n_channels == 3
                elif k == 1:
                    channel_options_wid.children[1].children[0].children[0].value = "Single"
                elif k == 2:
                    channel_options_wid.children[1].children[1].children[0].children[0].value = 0
                else:
                    channel_options_wid.children[1].children[1].children[0].children[1].value = 0


def landmark_options(landmark_options_default, plot_function=None,
                     toggle_show_default=True, toggle_show_visible=True):
    r"""
    Creates a widget with Landmark Options. Specifically, it has:
        1) A checkbox that controls the landmarks' visibility.
        2) A drop down menu with the available landmark groups.
        3) Several toggle buttons with the group's available labels.
        4) A toggle button that controls the visibility of all the above, i.e.
           the landmark options.

    The structure of the widgets is the following:
        landmark_options_wid.children = [toggle_button, landmarks_checkbox,
                                         groups]
        groups.children = [group_drop_down_menu, labels]
        labels.children = [labels_text, labels_toggle_buttons]

    The returned widget saves the selected values in the following dictionary:
        landmark_options_wid.selected_values

    To fix the alignment within this widget, please refer to
    `format_landmark_options()` function.

    To update the state of this widget, please refer to
    `update_landmark_options()` function.

    Parameters
    ----------
    landmark_options_default : `dict`
        The default options. For example:
            landmark_options_default = {'render_landmarks': True,
                                        'group_keys': ['PTS', 'ibug_face_68'],
                                        'labels_keys': [['all'], ['jaw', 'nose'],
                                        'group': 'PTS',
                                        'with_labels': ['all']}
    plot_function : `function` or None, optional
        The plot function that is executed when a widgets' value changes.
        If None, then nothing is assigned.
    toggle_show_default : `bool`, optional
        Defines whether the options will be visible upon construction.
    toggle_show_visible : `bool`, optional
        The visibility of the toggle button.
    """
    # Create all necessary widgets
    but = ToggleButtonWidget(description='Landmarks Options',
                             value=toggle_show_default,
                             visible=toggle_show_visible)
    landmarks = CheckboxWidget(description='Render landmarks',
                               value=landmark_options_default['render_landmarks'])
    group = DropdownWidget(values=landmark_options_default['group_keys'],
                           description='Group')
    labels_toggles = [[ToggleButtonWidget(description=k, value=True)
                       for k in s_keys]
                      for s_keys in landmark_options_default['labels_keys']]
    labels_text = LatexWidget(value='Labels')
    labels = ContainerWidget(children=labels_toggles[0])

    # Group widgets
    labels_and_text = ContainerWidget(children=[labels_text, labels])
    group_wid = ContainerWidget(children=[group, labels_and_text])

    # Widget container
    landmark_options_wid = ContainerWidget(children=[but, landmarks, group_wid])

    # Initialize output variables
    landmark_options_wid.selected_values = landmark_options_default
    landmark_options_wid.selected_values['labels_toggles'] = labels_toggles
    landmark_options_wid.selected_values['group'] = \
        landmark_options_wid.selected_values['group_keys'][0]
    landmark_options_wid.selected_values['with_labels'] = \
        landmark_options_wid.selected_values['labels_keys'][0]

    # Disability control
    def landmarks_fun(name, value):
        # get landmarks_enabled value
        landmark_options_wid.selected_values['render_landmarks'] = value
        # disable group drop down menu
        group.disabled = not value
        # disable all labels toggles
        for s_keys in landmark_options_wid.selected_values['labels_toggles']:
            for k in s_keys:
                k.disabled = not value
        # if all currently selected labels toggles are False, set them all
        # to True
        all_values = [ww.value for ww in labels.children]
        if all(item is False for item in all_values):
            for ww in labels.children:
                ww.value = True
    landmarks_fun('', landmark_options_wid.selected_values['render_landmarks'])
    landmarks.on_trait_change(landmarks_fun, 'value')

    # Group drop down method
    def group_fun(name, value):
        # get group value
        landmark_options_wid.selected_values['group'] = value
        # assign the correct children to the labels toggles
        labels.children = landmark_options_wid.selected_values['labels_toggles'][landmark_options_wid.selected_values['group_keys'].index(value)]
        # get with_labels value
        landmark_options_wid.selected_values['with_labels'] = []
        for ww in labels.children:
            if ww.value:
                landmark_options_wid.selected_values['with_labels'].append(
                    str(ww.description))
        # assign plot_function to all enabled labels
        if plot_function is not None:
            for w in labels.children:
                w.on_trait_change(plot_function, 'value')

    group.on_trait_change(group_fun, 'value')

    # Labels function
    def labels_fun(name, value):
        # if all labels toggles are False, set landmarks checkbox to False
        all_values = [ww.value for ww in labels.children]
        if all(item is False for item in all_values):
            landmarks.value = False
        # get with_labels value
        landmark_options_wid.selected_values['with_labels'] = []
        for ww in labels.children:
            if ww.value:
                landmark_options_wid.selected_values['with_labels'].append(
                    str(ww.description))
    # assign labels_fun to all labels toggles (even hidden ones)
    for s_group in landmark_options_wid.selected_values['labels_toggles']:
        for w in s_group:
            w.on_trait_change(labels_fun, 'value')

    # Toggle button function
    def show_options(name, value):
        group_wid.visible = value
        landmarks.visible = value
    show_options('', toggle_show_default)
    but.on_trait_change(show_options, 'value')

    # assign plot_function
    if plot_function is not None:
        # assign plot_function to landmarks checkbox and group drop down menu
        landmarks.on_trait_change(plot_function, 'value')
        group.on_trait_change(plot_function, 'value')
        # assign plot_function to all currently active labels toggles
        for w in labels.children:
            w.on_trait_change(plot_function, 'value')

    return landmark_options_wid


def format_landmark_options(landmark_options_wid, container_padding='6px',
                            container_margin='6px',
                            container_border='1px solid black',
                            toggle_button_font_weight='bold',
                            border_visible=True):
    r"""
    Function that corrects the align (style format) of a given landmark_options
    widget. Usage example:
        landmark_options_wid = landmark_options()
        display(landmark_options_wid)
        format_landmark_options(landmark_options_wid)

    Parameters
    ----------
    landmark_options_wid :
        The widget object generated by the `landmark_options()` function.

    container_padding : `str`, optional
        The padding around the widget, e.g. '6px'

    container_margin : `str`, optional
        The margin around the widget, e.g. '6px'

    container_border : `str`, optional
        The border around the widget, e.g. '1px solid black'

    toggle_button_font_weight : `str`
        The font weight of the toggle button, e.g. 'bold'

    border_visible : `boolean`, optional
        Defines whether to draw the border line around the widget.
    """
    # align labels toggle buttons
    landmark_options_wid.children[2].children[1].children[1].remove_class('vbox')
    landmark_options_wid.children[2].children[1].children[1].add_class('hbox')

    # align labels buttons with text
    landmark_options_wid.children[2].children[1].children[0].set_css(
        'margin-right', '5px')
    landmark_options_wid.children[2].children[1].remove_class('vbox')
    landmark_options_wid.children[2].children[1].add_class('hbox')
    landmark_options_wid.children[2].children[1].add_class('align-center')

    # align group drop down menu with labels toggle buttons
    landmark_options_wid.children[2].children[1].set_css('margin-top', '10px')
    landmark_options_wid.children[2].add_class('align-start')

    # set toggle button font bold
    landmark_options_wid.children[0].set_css('font-weight',
                                             toggle_button_font_weight)

    # margin and border around container widget
    landmark_options_wid.set_css('padding', container_padding)
    landmark_options_wid.set_css('margin', container_margin)
    if border_visible:
        landmark_options_wid.set_css('border', container_border)


def update_landmark_options(landmark_options_wid, group_keys, labels_keys,
                            plot_function):
    r"""
    Function that updates the state of a given landmark_options widget if the
    group or label keys of an image has changed. Usage example:
        landmark_options_default = {'render_landmarks': True,
                                    'group_keys': ['PTS', 'ibug_face_68'],
                                    'labels_keys': [['all'], ['jaw', 'nose'],
                                    'group': 'PTS',
                                    'with_labels': ['all']}
        landmark_options_wid = landmark_options(landmark_options_default)
        display(landmark_options_wid)
        format_landmark_options(landmark_options_wid)
        update_landmark_options(landmark_options_wid,
                                group_keys=['group3'],
                                labels_keys=['label31', 'label32', 'label33'])
        format_landmark_options(landmark_options_wid)

    Note that the `format_landmark_options()` function needs to be called again
    after the `update_landmark_options()` function.

    Parameters
    ----------
    landmark_options_wid :
        The widget object generated by the `landmark_options()` function.

    group_keys : `list` of `str`
        A list of the available landmark groups.

    labels_keys : `list` of `list` of `str`
        A list of lists of each landmark group's labels.

    plot_function : `function` or None
        The plot function that is executed when a widgets' value changes.
        If None, then nothing is assigned.
    """
    # check if the new group_keys and labels_keys are the same as the old
    # ones
    if not _compare_groups_and_labels(
            group_keys, labels_keys,
            landmark_options_wid.selected_values['group_keys'],
            landmark_options_wid.selected_values['labels_keys']):
        # Create all necessary widgets
        group = DropdownWidget(values=group_keys, description='Group')
        labels_toggles = [[ToggleButtonWidget(description=k, value=True)
                           for k in s_keys] for s_keys in labels_keys]

        # Group widgets
        landmark_options_wid.children[2].children[1].children[1].\
            children = labels_toggles[0]
        labels = landmark_options_wid.children[2].children[1]
        cont = ContainerWidget(children=[group, labels])
        landmark_options_wid.children = [landmark_options_wid.children[0],
                                         landmark_options_wid.children[1],
                                         cont]

        # Initialize output variables
        landmark_options_wid.selected_values['group_keys'] = group_keys
        landmark_options_wid.selected_values['labels_keys'] = labels_keys
        landmark_options_wid.selected_values['labels_toggles'] = labels_toggles
        landmark_options_wid.selected_values['group'] = group_keys[0]
        landmark_options_wid.selected_values['with_labels'] = labels_keys[0]

        # Disability control
        def landmarks_fun(name, value):
            # get landmarks_enabled value
            landmark_options_wid.selected_values['render_landmarks'] = value
            # disable group drop down menu
            group.disabled = not value
            # disable all labels toggles
            for s_keys in landmark_options_wid.selected_values['labels_toggles']:
                for k in s_keys:
                    k.disabled = not value
            # if all currently selected labels toggles are False, set them all
            # to True
            all_values = [ww.value
                          for ww in landmark_options_wid.children[2].children[1].children[1].children]
            if all(item is False for item in all_values):
                for ww in landmark_options_wid.children[2].children[1].children[1].children:
                    ww.value = True
        landmark_options_wid.children[1].on_trait_change(landmarks_fun, 'value')
        landmarks_fun('',
                      landmark_options_wid.selected_values['render_landmarks'])

        # Group drop down method
        def group_fun(name, value):
            # get group value
            landmark_options_wid.selected_values['group'] = value
            # assign the correct children to the labels toggles
            landmark_options_wid.children[2].children[1].children[1].\
                children = landmark_options_wid.selected_values['labels_toggles'][
                    landmark_options_wid.selected_values['group_keys'].index(value)]
            # get with_labels value
            landmark_options_wid.selected_values['with_labels'] = []
            for ww in landmark_options_wid.children[2].children[1].children[1].children:
                if ww.value:
                    landmark_options_wid.selected_values['with_labels'].append(
                        str(ww.description))
            # assign plot_function to all enabled labels
            if plot_function is not None:
                for w in landmark_options_wid.children[2].children[1].children[1].children:
                    w.on_trait_change(plot_function, 'value')

        group.on_trait_change(group_fun, 'value')

        # Labels function
        def labels_fun(name, value):
            # if all labels toggles are False, set landmarks checkbox to False
            all_values = [ww.value
                          for ww in landmark_options_wid.children[2].children[1].children[1].children]
            if all(item is False for item in all_values):
                landmark_options_wid.children[1].value = False
            # get with_labels value
            landmark_options_wid.selected_values['with_labels'] = []
            for ww in landmark_options_wid.children[2].children[1].children[1].\
                    children:
                if ww.value:
                    landmark_options_wid.selected_values['with_labels'].append(
                        str(ww.description))
        # assign labels_fun to all labels toggles (even hidden ones)
        for s_group in labels_toggles:
            for w in s_group:
                w.on_trait_change(labels_fun, 'value')

        # assign plot_function
        if plot_function is not None:
            # assign plot_function to landmarks checkbox, legend
            # checkbox and group drop down menu
            group.on_trait_change(plot_function, 'value')
            # assign plot_function to all currently active labels toggles
            for w in labels_toggles[0]:
                w.on_trait_change(plot_function, 'value')

        # Toggle button function
        def show_options(name, value):
            landmark_options_wid.children[1].visible = value
            landmark_options_wid.children[2].visible = value
        show_options('', landmark_options_wid.children[0].value)
        landmark_options_wid.children[0].on_trait_change(show_options, 'value')

        # If there is only one group with value ' ', this means that the image
        # didn't have any landmarks. So disable the show_landmarks checkbox.
        if len(group_keys) == 1 and group_keys[0] == ' ':
            # No landmarks are provided. So disable the show landmarks checkbox
            landmark_options_wid.children[1].value = False
            landmark_options_wid.children[1].disabled = True
        else:
            if landmark_options_wid.children[1].disabled:
                landmark_options_wid.children[1].disabled = False
                landmark_options_wid.children[1].value = True


def info_print(toggle_show_default=True, toggle_show_visible=True):
    r"""
    Creates a widget that can print information. Specifically, it has:
        1) A latex widget where user can write the info text in latex format.
        2) A toggle button that controls the visibility of all the above, i.e.
           the info printing.

    The structure of the widgets is the following:
        info_wid.children = [toggle_button, text_widget]

    Parameters
    ----------
    toggle_show_default : `boolean`, optional
        Defines whether the info will be visible upon construction.

    toggle_show_visible : `boolean`, optional
        The visibility of the toggle button.
    """
    # Create toggle button
    but = ToggleButtonWidget(description='Info', value=toggle_show_default,
                             visible=toggle_show_visible)

    # Create text widget
    text_wid = LatexWidget(value="$\\bullet~$")

    # Toggle button function
    def show_options(name, value):
        text_wid.visible = value
    show_options('', toggle_show_default)
    but.on_trait_change(show_options, 'value')

    # Group widgets
    info_wid = ContainerWidget(children=[but, text_wid])

    return info_wid


def format_info_print(info_wid, font_size_in_pt='9pt', container_padding='6px',
                      container_margin='6px',
                      container_border='1px solid black',
                      toggle_button_font_weight='bold',
                      border_visible=True):
    r"""
    Function that corrects the align (style format) of a given info widget.
    Usage example:
        info_wid = info_print()
        display(info_wid)
        format_info_print(info_wid)

    Parameters
    ----------
    info_wid :
        The widget object generated by the `info_print()` function.

    font_size_in_pt : `str`, optional
        The font size of the latex text, e.g. '9pt'

    container_padding : `str`, optional
        The padding around the widget, e.g. '6px'

    container_margin : `str`, optional
        The margin around the widget, e.g. '6px'

    container_border : `str`, optional
        The border around the widget, e.g. '1px solid black'

    toggle_button_font_weight : `str`
        The font weight of the toggle button, e.g. 'bold'

    border_visible : `boolean`, optional
        Defines whether to draw the border line around the widget.
    """
    # latex widget formatting
    info_wid.children[1].set_css({'border': '1px dashed gray',
                                  'padding': '4px',
                                  'margin-top': '5px',
                                  'font-size': font_size_in_pt})

    # set toggle button font bold
    info_wid.children[0].set_css('font-weight', toggle_button_font_weight)

    # margin and border around container widget
    info_wid.set_css('padding', container_padding)
    info_wid.set_css('margin', container_margin)
    if border_visible:
        info_wid.set_css('border', container_border)


def model_parameters(n_params, plot_function=None, params_str='',
                     mode='multiple', params_bounds=(-3., 3.),
                     plot_eig_visible=True, plot_eig_function=None,
                     toggle_show_default=True, toggle_show_visible=True,
                     toggle_show_name='Parameters'):
    r"""
    Creates a widget with Model Parameters. Specifically, it has:
        1) A slider for each parameter if mode is 'multiple'.
        2) A single slider and a drop down menu selection if mode is 'single'.
        3) A reset button.
        4) A button and two radio buttons for plotting the eigenvalues variance
           ratio.

    The structure of the widgets is the following:
        model_parameters_wid.children = [toggle_button, parameters_and_reset]
        parameters_and_reset.children = [parameters_widgets, reset]
        If plot_eig_visible is True:
            reset = [plot_eigenvalues, reset_button]
        Else:
            reset = reset_button
        If mode is single:
            parameters_widgets.children = [drop_down_menu, slider]
        If mode is multiple:
            parameters_widgets.children = [all_sliders]

    The returned widget saves the selected values in the following fields:
        model_parameters_wid.parameters_values
        model_parameters_wid.mode
        model_parameters_wid.plot_eig_visible

    To fix the alignment within this widget please refer to
    `format_model_parameters()` function.

    To update the state of this widget, please refer to
    `update_model_parameters()` function.

    Parameters
    ----------
    n_params : `int`
        The number of principal components to use for the sliders.

    plot_function : `function` or None, optional
        The plot function that is executed when a widgets' value changes.
        If None, then nothing is assigned.

    params_str : `str`, optional
        The string that will be used for each parameters name.

    mode : 'single' or 'multiple', optional
        If single, only a single slider is constructed along with a drop down
        menu.
        If multiple, a slider is constructed for each parameter.

    params_bounds : (`float`, `float`), optional
        The minimum and maximum bounds, in std units, for the sliders.

    plot_eig_visible : `boolean`, optional
        Defines whether the options for plotting the eigenvalues variance ratio
        will be visible upon construction.

    plot_eig_function : `function` or None, optional
        The plot function that is executed when the plot eigenvalues button is
        clicked. If None, then nothing is assigned.

    toggle_show_default : `boolean`, optional
        Defines whether the options will be visible upon construction.

    toggle_show_visible : `boolean`, optional
        The visibility of the toggle button.

    toggle_show_name : `str`, optional
        The name of the toggle button.
    """
    # If only one slider requested, then set mode to multiple
    if n_params == 1:
        mode = 'multiple'

    # Create all necessary widgets
    but = ToggleButtonWidget(description=toggle_show_name,
                             value=toggle_show_default,
                             visible=toggle_show_visible)
    reset_button = ButtonWidget(description='Reset')
    if mode == 'multiple':
        sliders = [FloatSliderWidget(description="{}{}".format(params_str, p),
                                     min=params_bounds[0], max=params_bounds[1],
                                     value=0.)
                   for p in range(n_params)]
        parameters_wid = ContainerWidget(children=sliders)
    else:
        vals = OrderedDict()
        for p in range(n_params):
            vals["{}{}".format(params_str, p)] = p
        slider = FloatSliderWidget(description='', min=params_bounds[0],
                                   max=params_bounds[1], value=0.)
        dropdown_params = DropdownWidget(values=vals)
        parameters_wid = ContainerWidget(children=[dropdown_params, slider])

    # Group widgets
    if plot_eig_visible:
        plot_button = ButtonWidget(description='Plot eigenvalues')
        if plot_eig_function is not None:
            plot_button.on_click(plot_eig_function)
        plot_and_reset = ContainerWidget(children=[plot_button, reset_button])
        params_and_reset = ContainerWidget(children=[parameters_wid,
                                                     plot_and_reset])
    else:
        params_and_reset = ContainerWidget(children=[parameters_wid,
                                                     reset_button])

    # Widget container
    model_parameters_wid = ContainerWidget(children=[but, params_and_reset])

    # Save mode and parameters values
    model_parameters_wid.parameters_values = [0.0] * n_params
    model_parameters_wid.mode = mode
    model_parameters_wid.plot_eig_visible = plot_eig_visible

    # set up functions
    if mode == 'single':
        # assign slider value to parameters values list
        def save_slider_value(name, value):
            model_parameters_wid.parameters_values[dropdown_params.value] = \
                value
        slider.on_trait_change(save_slider_value, 'value')

        # set correct value to slider when drop down menu value changes
        def set_slider_value(name, value):
            slider.value = model_parameters_wid.parameters_values[value]
        dropdown_params.on_trait_change(set_slider_value, 'value')

        # assign main plotting function when slider value changes
        if plot_function is not None:
            slider.on_trait_change(plot_function, 'value')
    else:
        # assign slider value to parameters values list
        def save_slider_value_from_id(description, name, value):
            i = int(description[len(params_str)::])
            model_parameters_wid.parameters_values[i] = value

        # partial function that helps get the widget's description str
        def partial_widget(description):
            return lambda name, value: save_slider_value_from_id(description,
                                                                 name, value)

        # assign saving values and main plotting function to all sliders
        for w in parameters_wid.children:
            # The widget (w) is lexically scoped and so we need a way of
            # ensuring that we don't just receive the final value of w at every
            # iteration. Therefore we create another lambda function that
            # creates a new lexical scoping so that we can ensure the value of w
            # is maintained (as x) at each iteration.
            # In JavaScript, we would just use the 'let' keyword...
            w.on_trait_change(partial_widget(w.description), 'value')
            if plot_function is not None:
                w.on_trait_change(plot_function, 'value')

    # reset function
    def reset_params(name):
        model_parameters_wid.parameters_values = \
            [0.0] * len(model_parameters_wid.parameters_values)
        if mode == 'multiple':
            for ww in parameters_wid.children:
                ww.value = 0.
        else:
            parameters_wid.children[0].value = 0
            parameters_wid.children[1].value = 0.
    reset_button.on_click(reset_params)

    # Toggle button function
    def show_options(name, value):
        params_and_reset.visible = value
    show_options('', toggle_show_default)
    but.on_trait_change(show_options, 'value')

    return model_parameters_wid


def format_model_parameters(model_parameters_wid, container_padding='6px',
                            container_margin='6px',
                            container_border='1px solid black',
                            toggle_button_font_weight='bold',
                            border_visible=True):
    r"""
    Function that corrects the align (style format) of a given model_parameters
    widget. Usage example:
        model_parameters_wid = model_parameters()
        display(model_parameters_wid)
        format_model_parameters(model_parameters_wid)

    Parameters
    ----------
    model_parameters_wid :
        The widget object generated by the `model_parameters()` function.

    container_padding : `str`, optional
        The padding around the widget, e.g. '6px'

    container_margin : `str`, optional
        The margin around the widget, e.g. '6px'

    container_border : `str`, optional
        The border around the widget, e.g. '1px solid black'

    toggle_button_font_weight : `str`
        The font weight of the toggle button, e.g. 'bold'

    border_visible : `boolean`, optional
        Defines whether to draw the border line around the widget.
    """
    if model_parameters_wid.mode == 'single':
        # align drop down menu and slider
        model_parameters_wid.children[1].children[0].remove_class('vbox')
        model_parameters_wid.children[1].children[0].add_class('hbox')
    else:
        # align sliders
        model_parameters_wid.children[1].children[0].add_class('start')

    # align reset button to right
    if model_parameters_wid.plot_eig_visible:
        model_parameters_wid.children[1].children[1].remove_class('vbox')
        model_parameters_wid.children[1].children[1].add_class('hbox')
    model_parameters_wid.children[1].add_class('align-end')

    # set toggle button font bold
    model_parameters_wid.children[0].set_css('font-weight',
                                             toggle_button_font_weight)

    # margin and border around plot_eigenvalues widget
    if model_parameters_wid.plot_eig_visible:
        model_parameters_wid.children[1].children[1].children[0].set_css(
            'margin-right', container_margin)

    # margin and border around container widget
    model_parameters_wid.set_css('padding', container_padding)
    model_parameters_wid.set_css('margin', container_margin)
    if border_visible:
        model_parameters_wid.set_css('border', container_border)


def update_model_parameters(model_parameters_wid, n_params, plot_function=None,
                            params_str=''):
    r"""
    Function that updates the state of a given model_parameters widget if the
    requested number of parameters has changed. Usage example:
        model_parameters_wid = model_parameters(n_params=5)
        display(model_parameters_wid)
        format_model_parameters(model_parameters_wid)
        update_model_parameters(model_parameters_wid, 3)

    Parameters
    ----------
    model_parameters_wid :
        The widget object generated by the `model_parameters()` function.

    n_params : `int`
        The requested number of parameters.

    plot_function : `function` or None, optional
        The plot function that is executed when a widgets' value changes.
        If None, then nothing is assigned.

    params_str : `str`, optional
        The string that will be used for each parameters name.
    """
    if model_parameters_wid.mode == 'multiple':
        # get the number of enabled parameters (number of sliders)
        enabled_params = len(model_parameters_wid.children[1].children[0].children)
        if n_params != enabled_params:
            # reset all parameters values
            model_parameters_wid.parameters_values = [0.0] * n_params
            # get params_bounds
            pb = [model_parameters_wid.children[1].children[0].children[0].min,
                  model_parameters_wid.children[1].children[0].children[0].max]
            # create sliders widgets
            sliders = [FloatSliderWidget(description="{}{}".format(params_str,
                                                                   p),
                                         min=pb[0], max=pb[1], value=0.)
                       for p in range(n_params)]
            # assign sliders to container
            model_parameters_wid.children[1].children[0].children = sliders

            # assign slider value to parameters values list
            def save_slider_value_from_id(description, name, value):
                i = int(description[len(params_str)::])
                model_parameters_wid.parameters_values[i] = value

            # partial function that helps get the widget's description str
            def partial_widget(description):
               return lambda name, value: save_slider_value_from_id(description,
                                                                    name, value)

            # assign saving values and main plotting function to all sliders
            for w in model_parameters_wid.children[1].children[0].children:
                # The widget (w) is lexically scoped and so we need a way of
                # ensuring that we don't just receive the final value of w at
                # every iteration. Therefore we create another lambda function
                # that creates a new lexical scoping so that we can ensure the
                # value of w is maintained (as x) at each iteration
                # In JavaScript, we would just use the 'let' keyword...
                w.on_trait_change(partial_widget(w.description), 'value')
                if plot_function is not None:
                    w.on_trait_change(plot_function, 'value')
    else:
        # get the number of enabled parameters (len of list of drop down menu)
        enabled_params = len(model_parameters_wid.children[1].children[0].children[0].values)
        if n_params != enabled_params:
            # reset all parameters values
            model_parameters_wid.parameters_values = [0.0] * n_params
            # change drop down menu values
            vals = OrderedDict()
            for p in range(n_params):
                vals["{}{}".format(params_str, p)] = p
            model_parameters_wid.children[1].children[0].children[0].values = \
                vals
            # set initial value to the first and slider value to zero
            model_parameters_wid.children[1].children[0].children[0].value = \
                vals["{}{}".format(params_str, 0)]
            model_parameters_wid.children[1].children[0].children[1].value = 0.


def final_result_options(group_keys, plot_function=None, title='Final Result',
                         show_image_default=True,
                         subplots_enabled_default=False, legend_default=True,
                         numbering_default=True,
                         toggle_show_default=True, toggle_show_visible=True):
    r"""
    Creates a widget with Final Result Options. Specifically, it has:
        1) A set of toggle buttons representing usually the initial, final and
           ground truth shapes.
        2) A checkbox that controls the visibility of the image.
        3) A set of radio buttons that define whether subplots are enabled.
        4) A checkbox that controls the legend's visibility.
        5) A checkbox that controls the numbering visibility.
        6) A toggle button that controls the visibility of all the above, i.e.
           the final result options.

    The structure of the widgets is the following:
        final_result_wid.children = [toggle_button, shapes_toggle_buttons,
                                     show_image_checkbox, options]
        options.children = [plot_mode_radio_buttons, legend_checkbox,
                            numbering_checkbox]

    The returned widget saves the selected values in the following fields:
        final_result_wid.all_group_keys
        final_result_wid.groups
        final_result_wid.show_image
        final_result_wid.subplots_enabled
        final_result_wid.legend_enabled
        final_result_wid.numbering_enabled

    To fix the alignment within this widget please refer to
    `format_final_result_options()` function.

    Parameters
    ----------
    group_keys : `list` of `str`
        A list of the available landmark groups.
    plot_function : `function` or None, optional
        The plot function that is executed when a widgets' value changes.
        If None, then nothing is assigned.
    title : `str`, optional
        The title of the widget printed at the toggle button.
    show_image_default : `bool`, optional
        The initial value of the image's visibility checkbox.
    subplots_enabled_default : `bool`, optional
        The initial value of the plot options' radio buttons that determine
        whether a single plot or subplots will be used.
    legend_default : `bool`, optional
        The initial value of the legend's visibility checkbox.
    numbering_default : `bool`, optional
        The initial value of the numbering visibility checkbox.
    toggle_show_default : `bool`, optional
        Defines whether the options will be visible upon construction.
    toggle_show_visible : `bool`, optional
        The visibility of the toggle button.
    """
    # Toggle button that controls options' visibility
    but = ToggleButtonWidget(description=title,
                             value=toggle_show_default,
                             visible=toggle_show_visible)

    # Create widgets
    shapes_checkboxes = [LatexWidget(value='Select shape:')]
    for group in group_keys:
        t = ToggleButtonWidget(description=group, value=False)
        if group == 'final':
            t.value = True
        shapes_checkboxes.append(t)
    show_image = CheckboxWidget(description='Show image',
                                value=show_image_default)
    mode = RadioButtonsWidget(description='Plot mode:',
                              values={'Single': False, 'Multiple': True})
    mode.value = subplots_enabled_default
    show_legend = CheckboxWidget(description='Show legend',
                                 value=legend_default)
    show_numbering = CheckboxWidget(description='Show numbering',
                                    value=numbering_default)

    # Group widgets
    shapes_wid = ContainerWidget(children=shapes_checkboxes)
    opts = ContainerWidget(children=[mode, show_legend, show_numbering])

    # Widget container
    final_result_wid = ContainerWidget(children=[but, shapes_wid, show_image,
                                                 opts])

    # Initialize variables
    final_result_wid.all_group_keys = group_keys
    final_result_wid.groups = ['final']
    final_result_wid.show_image = show_image_default
    final_result_wid.subplots_enabled = subplots_enabled_default
    final_result_wid.legend_enabled = legend_default
    final_result_wid.numbering_enabled = numbering_default

    # Groups function
    def groups_fun(name, value):
        final_result_wid.groups = []
        for i in shapes_wid.children[1::]:
            if i.value:
                final_result_wid.groups.append(str(i.description))
    for w in shapes_wid.children[1::]:
        w.on_trait_change(groups_fun, 'value')

    # Show image function
    def show_image_fun(name, value):
        final_result_wid.show_image = value
    show_image.on_trait_change(show_image_fun, 'value')

    # Plot mode function
    def plot_mode_fun(name, value):
        final_result_wid.subplots_enabled = value
    mode.on_trait_change(plot_mode_fun, 'value')

    # Legend function
    def legend_fun(name, value):
        final_result_wid.legend_enabled = value
    show_legend.on_trait_change(legend_fun, 'value')

    # Numbering function
    def numbering_fun(name, value):
        final_result_wid.numbering_enabled = value
    show_numbering.on_trait_change(numbering_fun, 'value')

    # Toggle button function
    def show_options(name, value):
        shapes_wid.visible = value
        show_image.visible = value
        opts.visible = value
    show_options('', toggle_show_default)
    but.on_trait_change(show_options, 'value')

    # assign plot_function
    if plot_function is not None:
        show_image.on_trait_change(plot_function, 'value')
        mode.on_trait_change(plot_function, 'value')
        show_legend.on_trait_change(plot_function, 'value')
        show_numbering.on_trait_change(plot_function, 'value')
        for w in shapes_wid.children[1::]:
            w.on_trait_change(plot_function, 'value')

    return final_result_wid


def format_final_result_options(final_result_wid, container_padding='6px',
                                container_margin='6px',
                                container_border='1px solid black',
                                toggle_button_font_weight='bold',
                                border_visible=True):
    r"""
    Function that corrects the align (style format) of a given
    final_result_options widget. Usage example:
        final_result_wid = final_result_options()
        display(final_result_wid)
        format_final_result_options(final_result_wid)

    Parameters
    ----------
    final_result_wid :
        The widget object generated by the `final_result_options()` function.

    container_padding : `str`, optional
        The padding around the widget, e.g. '6px'

    container_margin : `str`, optional
        The margin around the widget, e.g. '6px'

    container_border : `str`, optional
        The border around the widget, e.g. '1px solid black'

    toggle_button_font_weight : `str`
        The font weight of the toggle button, e.g. 'bold'

    border_visible : `boolean`, optional
        Defines whether to draw the border line around the widget.
    """
    # align shapes toggle buttons
    final_result_wid.children[1].remove_class('vbox')
    final_result_wid.children[1].add_class('hbox')
    final_result_wid.children[1].add_class('align-center')
    final_result_wid.children[1].children[0].set_css('margin-right',
                                                     container_margin)

    # align mode and legend options
    final_result_wid.children[3].remove_class('vbox')
    final_result_wid.children[3].add_class('hbox')
    final_result_wid.children[3].children[0].set_css('margin-right', '20px')

    # set toggle button font bold
    final_result_wid.children[0].set_css('font-weight',
                                         toggle_button_font_weight)
    final_result_wid.children[1].set_css('margin-top', container_margin)

    # margin and border around container widget
    final_result_wid.set_css('padding', container_padding)
    final_result_wid.set_css('margin', container_margin)
    if border_visible:
        final_result_wid.set_css('border', container_border)


def update_final_result_options(final_result_wid, group_keys, plot_function):
    r"""
    Function that updates the state of a given final_result_options widget if
    the group keys of an image has changed. Usage example:
        group_keys = ['group1', 'group2']
        final_result_wid = final_result_options(group_keys=group_keys)
        display(final_result_wid)
        format_final_result_options(final_result_wid)
        update_final_result_options(final_result_wid,
                                    group_keys=['group3'])
        format_final_result_options(final_result_wid)

    Note that the `format_final_result_options()` function needs to be called
    again after the `update_final_result_options()` function.

    Parameters
    ----------
    final_result_wid :
        The widget object generated by the `final_result_options()` function.

    group_keys : `list` of `str`
        A list of the available landmark groups.

    plot_function : `function` or None
        The plot function that is executed when a widgets' value changes.
        If None, then nothing is assigned.
    """
    # check if the new group_keys are the same as the old ones
    if not _compare_groups_and_labels(group_keys, [],
                                      final_result_wid.all_group_keys, []):
        # Create all necessary widgets
        shapes_checkboxes = [LatexWidget(value='Select shape:')]
        for group in group_keys:
            t = ToggleButtonWidget(description=group, value=True)
            shapes_checkboxes.append(t)

        # Group widgets
        final_result_wid.children[1].children = shapes_checkboxes

        # Initialize output variables
        final_result_wid.all_group_keys = group_keys
        final_result_wid.groups = group_keys

        # Groups function
        def groups_fun(name, value):
            final_result_wid.groups = []
            for i in final_result_wid.children[1].children[1::]:
                if i.value:
                    final_result_wid.groups.append(str(i.description))
        for w in final_result_wid.children[1].children[1::]:
            w.on_trait_change(groups_fun, 'value')

        # Toggle button function
        def show_options(name, value):
            final_result_wid.children[1].visible = value
            final_result_wid.children[2].visible = value
            final_result_wid.children[3].visible = value
        show_options('', final_result_wid.children[0].value)
        final_result_wid.children[0].on_trait_change(show_options, 'value')

        # assign plot_function
        if plot_function is not None:
            final_result_wid.children[2].on_trait_change(plot_function, 'value')
            final_result_wid.children[3].children[0].on_trait_change(
                plot_function, 'value')
            final_result_wid.children[3].children[1].on_trait_change(
                plot_function, 'value')
            for w in final_result_wid.children[1].children[1::]:
                w.on_trait_change(plot_function, 'value')


def iterations_result_options(n_iters, image_has_gt_shape, n_points,
                              plot_function=None, plot_errors_function=None,
                              plot_displacements_function=None,
                              iter_str='iter_', title='Iterations Result',
                              show_image_default=True,
                              subplots_enabled_default=False,
                              numbering_default=False,
                              legend_default=True, toggle_show_default=True,
                              toggle_show_visible=True):
    r"""
    Creates a widget with Iterations Result Options. Specifically, it has:
        1) Two radio buttons that select an options mode, depending on whether
           the user wants to visualize iterations in "Animation" or "Static" mode.
        2) If mode is "Animation", an animation options widget appears.
           If mode is "Static", the iterations range is selected by two
           sliders and there is an update plot button.
        3) A checkbox that controls the visibility of the image.
        4) A set of radio buttons that define whether subplots are enabled.
        5) A checkbox that controls the legend's visibility.
        6) A checkbox that controls the numbering visibility.
        7) A button to plot the error evolution.
        8) A button to plot the landmark points' displacement.
        9) A drop down menu to select which displacement to plot.
        10) A toggle button that controls the visibility of all the above, i.e.
           the final result options.

    The structure of the widgets is the following:
        iterations_result_wid.children = [toggle_button,
                                          iterations_mode_and_sliders,
                                          options]
        iterations_mode_and_sliders.children = [iterations_mode_radio_buttons,
                                                all_sliders]
        all_sliders.children = [animation_slider, first_slider, second_slider,
                                update_button]
        options.children = [plot_mode_radio_buttons, show_image_checkbox,
                            show_legend_checkbox, plot_errors_button,
                            plot_displacements, show_numbering_checkbox]
        plot_displacements.children = [plot_displacements_button,
                                       plot_displacements_drop_down_menu]

    The returned widget saves the selected values in the following fields:
        iterations_result_wid.groups
        iterations_result_wid.image_has_gt_shape
        iterations_result_wid.n_iters
        iterations_result_wid.n_points
        iterations_result_wid.show_image
        iterations_result_wid.subplots_enabled
        iterations_result_wid.legend_enabled
        iterations_result_wid.numbering_enabled
        iterations_result_wid.displacement_type

    To fix the alignment within this widget please refer to
    `format_iterations_result_options()` function.

    To update the state of this widget, please refer to
    `update_iterations_result_options()` function.

    Parameters
    ----------
    n_iters : `int`
        The number of iterations.
    image_has_gt_shape : `bool`
        Flag that defines whether the fitted image has a ground shape attached.
    n_points : `int`
        The number of the object's  landmark points. It is required by the
        displacement dorp down menu.
    plot_function : `function` or None, optional
        The plot function that is executed when a widgets' value changes.
        If None, then nothing is assigned.
    plot_errors_function : `function` or None, optional
        The plot function that is executed when the 'Plot Errors' button is
        pressed.
        If None, then nothing is assigned.
    plot_displacements_function : `function` or None, optional
        The plot function that is executed when the 'Plot Displacements' button
        is pressed.
        If None, then nothing is assigned.
    iter_str : `str`, optional
        The str that is used in the landmark groups shapes.
        E.g. if iter_str == "iter_" then the group label of iteration i has the
        form "{}{}".format(iter_str, i)
    title : `str`, optional
        The title of the widget printed at the toggle button.
    show_image_default : `bool`, optional
        The initial value of the image's visibility checkbox.
    subplots_enabled_default : `bool`, optional
        The initial value of the plot options' radio buttons that determine
        whether a single plot or subplots will be used.
    legend_default : `bool`, optional
        The initial value of the legend's visibility checkbox.
    numbering_default : `bool`, optional
        The initial value of the numbering visibility checkbox.
    toggle_show_default : `bool`, optional
        Defines whether the options will be visible upon construction.
    toggle_show_visible : `bool`, optional
        The visibility of the toggle button.
    """
    # Create all necessary widgets
    but = ToggleButtonWidget(description=title, value=toggle_show_default,
                             visible=toggle_show_visible)
    iterations_mode = RadioButtonsWidget(values={'Animation': 0, 'Static': 1},
                                         value=0,
                                         description='Iterations mode:',
                                         visible=toggle_show_default)
    # Don't assign the plot function to the animation_wid at this point. We
    # first need to assign the get_groups function and then the plot_function()
    # for synchronization reasons.
    animation_wid = animation_options(index_min_val=0, index_max_val=n_iters-1,
                                      plot_function=None,
                                      update_function=None,
                                      index_step=1, index_default=0,
                                      index_description='Iteration',
                                      index_style='slider',
                                      loop_default=False, interval_default=0.2,
                                      toggle_show_default=toggle_show_default,
                                      toggle_show_visible=False)
    first_slider_wid = IntSliderWidget(min=0, max=n_iters-1, step=1,
                                       value=0, description='From',
                                       visible=False)
    second_slider_wid = IntSliderWidget(min=0, max=n_iters-1, step=1,
                                        value=n_iters-1, description='To',
                                        visible=False)
    update_but = ButtonWidget(description='Update Plot', visible=False)
    show_image = CheckboxWidget(description='Show image',
                                value=show_image_default)
    plot_errors_button = ButtonWidget(description='Plot Errors')
    plot_displacements_button = ButtonWidget(description='Plot Displacements')
    dropdown_menu = OrderedDict()
    dropdown_menu['mean'] = 'mean'
    dropdown_menu['median'] = 'median'
    dropdown_menu['max'] = 'max'
    dropdown_menu['min'] = 'min'
    for p in range(n_points):
        dropdown_menu["point {}".format(p)] = p
    plot_displacements_menu = SelectWidget(values=dropdown_menu, value='mean')
    plot_mode = RadioButtonsWidget(description='Plot mode:',
                                   values={'Single': False, 'Multiple': True})
    plot_mode.value = subplots_enabled_default
    show_legend = CheckboxWidget(description='Show legend',
                                 value=legend_default)
    show_numbering = CheckboxWidget(description='Show numbering',
                                    value=numbering_default)
    # if just one iteration, disable multiple options
    if n_iters == 1:
        iterations_mode.value = 0
        iterations_mode.disabled = True
        first_slider_wid.disabled = True
        animation_wid.children[1].children[0].children[2].disabled = True
        animation_wid.children[1].children[1].children[0].children[0].\
            disabled = True
        animation_wid.children[1].children[1].children[0].children[1].\
            disabled = True
        animation_wid.children[1].children[1].children[0].children[2].\
            disabled = True
        second_slider_wid.disabled = True
        plot_errors_button.disabled = True
        plot_displacements_button.disabled = True
        plot_displacements_menu.disabled = True

    # Group widgets
    sliders = ContainerWidget(children=[animation_wid, first_slider_wid,
                                        second_slider_wid, update_but])
    iterations_mode_and_sliders = ContainerWidget(children=[iterations_mode,
                                                            sliders])
    plot_displacements = ContainerWidget(children=[plot_displacements_button,
                                                   plot_displacements_menu])
    opts = ContainerWidget(children=[plot_mode, show_image, show_legend,
                                     show_numbering, plot_errors_button,
                                     plot_displacements])

    # Widget container
    iterations_result_wid = ContainerWidget(children=[
        but, iterations_mode_and_sliders, opts])

    # Initialize variables
    iterations_result_wid.groups = _convert_iterations_to_groups(0, 0, iter_str)
    iterations_result_wid.image_has_gt_shape = image_has_gt_shape
    iterations_result_wid.n_iters = n_iters
    iterations_result_wid.n_points = n_points
    iterations_result_wid.show_image = show_image_default
    iterations_result_wid.subplots_enabled = subplots_enabled_default
    iterations_result_wid.legend_enabled = legend_default
    iterations_result_wid.numbering_enabled = numbering_default
    iterations_result_wid.displacement_type = 'mean'

    # Define iterations mode visibility
    def iterations_mode_selection(name, value):
        if value == 0:
            # get val that needs to be assigned
            val = first_slider_wid.value
            # update visibility
            animation_wid.visible = True
            first_slider_wid.visible = False
            second_slider_wid.visible = False
            update_but.visible = False
            # set correct values
            animation_wid.children[1].children[0].children[2].value = val
            animation_wid.selected_index = val
            first_slider_wid.value = 0
            second_slider_wid.value = n_iters - 1
        else:
            # get val that needs to be assigned
            val = animation_wid.selected_index
            # update visibility
            animation_wid.visible = False
            first_slider_wid.visible = True
            second_slider_wid.visible = True
            update_but.visible = True
            # set correct values
            second_slider_wid.value = val
            first_slider_wid.value = val
            animation_wid.children[1].children[0].children[2].value = 0
            animation_wid.selected_index = 0
    iterations_mode.on_trait_change(iterations_mode_selection, 'value')

    # Check first slider's value
    def first_slider_val(name, value):
        if value > second_slider_wid.value:
            first_slider_wid.value = second_slider_wid.value
    first_slider_wid.on_trait_change(first_slider_val, 'value')

    # Check second slider's value
    def second_slider_val(name, value):
        if value < first_slider_wid.value:
            second_slider_wid.value = first_slider_wid.value
    second_slider_wid.on_trait_change(second_slider_val, 'value')

    # Convert slider values to groups
    def get_groups(name, value):
        if iterations_mode.value == 0:
            iterations_result_wid.groups = _convert_iterations_to_groups(
                animation_wid.selected_index,
                animation_wid.selected_index, iter_str)
        else:
            iterations_result_wid.groups = _convert_iterations_to_groups(
                first_slider_wid.value, second_slider_wid.value, iter_str)
    first_slider_wid.on_trait_change(get_groups, 'value')
    second_slider_wid.on_trait_change(get_groups, 'value')

    # assign get_groups() to the slider of animation_wid
    animation_wid.children[1].children[0].children[2].\
        on_trait_change(get_groups, 'value')

    # Show image function
    def show_image_fun(name, value):
        iterations_result_wid.show_image = value
    show_image.on_trait_change(show_image_fun, 'value')

    # Plot mode function
    def plot_mode_fun(name, value):
        iterations_result_wid.subplots_enabled = value
    plot_mode.on_trait_change(plot_mode_fun, 'value')

    # Legend function
    def legend_fun(name, value):
        iterations_result_wid.legend_enabled = value
    show_legend.on_trait_change(legend_fun, 'value')

    # Numbering function
    def numbering_fun(name, value):
        iterations_result_wid.numbering_enabled = value
    show_numbering.on_trait_change(numbering_fun, 'value')

    # Displacement type function
    def displacement_type_fun(name, value):
        iterations_result_wid.displacement_type = value
    plot_displacements_menu.on_trait_change(displacement_type_fun, 'value')

    # Toggle button function
    def show_options(name, value):
        iterations_mode.visible = value
        plot_mode.visible = value
        show_image.visible = value
        show_legend.visible = value
        show_numbering.visible = value
        plot_errors_button.visible = image_has_gt_shape and value
        plot_displacements.visible = value
        if value:
            if iterations_mode.value == 0:
                animation_wid.visible = True
            else:
                first_slider_wid.visible = True
                second_slider_wid.visible = True
        else:
            animation_wid.visible = False
            first_slider_wid.visible = False
            second_slider_wid.visible = False
    show_options('', toggle_show_default)
    but.on_trait_change(show_options, 'value')

    # assign general plot_function
    if plot_function is not None:
        def plot_function_but(name):
            plot_function(name, 0)
        update_but.on_click(plot_function_but)
        # Here we assign plot_function() to the slider of animation_wid, as
        # we didn't do it at its creation.
        animation_wid.children[1].children[0].children[2].on_trait_change(
            plot_function, 'value')
        show_image.on_trait_change(plot_function, 'value')
        plot_mode.on_trait_change(plot_function, 'value')
        show_legend.on_trait_change(plot_function, 'value')
        show_numbering.on_trait_change(plot_function, 'value')

    # assign plot function of errors button
    if plot_errors_function is not None:
        plot_errors_button.on_click(plot_errors_function)

    # assign plot function of displacements button
    if plot_displacements_function is not None:
        plot_displacements_button.on_click(plot_displacements_function)

    return iterations_result_wid


def format_iterations_result_options(iterations_result_wid,
                                     container_padding='6px',
                                     container_margin='6px',
                                     container_border='1px solid black',
                                     toggle_button_font_weight='bold',
                                     border_visible=True):
    r"""
    Function that corrects the align (style format) of a given
    iterations_result_options widget. Usage example:
        iterations_result_wid = iterations_result_options()
        display(iterations_result_wid)
        format_iterations_result_options(iterations_result_wid)

    Parameters
    ----------
    iterations_result_wid :
        The widget object generated by the `iterations_result_options()`
        function.
    container_padding : `str`, optional
        The padding around the widget, e.g. '6px'
    container_margin : `str`, optional
        The margin around the widget, e.g. '6px'
    container_border : `str`, optional
        The border around the widget, e.g. '1px solid black'
    toggle_button_font_weight : `str`
        The font weight of the toggle button, e.g. 'bold'
    border_visible : `bool`, optional
        Defines whether to draw the border line around the widget.
    """
    # format animations options
    format_animation_options(
        iterations_result_wid.children[1].children[1].children[0],
        index_text_width='0.5cm', container_padding=container_padding,
        container_margin=container_margin, container_border=container_border,
        toggle_button_font_weight=toggle_button_font_weight,
        border_visible=False)

    # align displacement button and drop down menu
    iterations_result_wid.children[2].children[5].add_class('align-center')
    iterations_result_wid.children[2].children[5].children[1].set_css('width',
                                                                      '2.5cm')
    iterations_result_wid.children[2].children[5].children[1].set_css('height',
                                                                      '2cm')

    # align options
    iterations_result_wid.children[2].remove_class('vbox')
    iterations_result_wid.children[2].add_class('hbox')
    iterations_result_wid.children[2].add_class('align-start')
    iterations_result_wid.children[2].children[0].set_css('margin-right',
                                                          '20px')
    iterations_result_wid.children[2].children[1].set_css('margin-right',
                                                          '10px')
    iterations_result_wid.children[2].children[2].set_css('margin-right',
                                                          '20px')
    iterations_result_wid.children[2].children[3].set_css('margin-right',
                                                          '20px')
    iterations_result_wid.children[2].children[4].set_css('margin-right',
                                                          '10px')

    # align sliders
    iterations_result_wid.children[1].children[1].add_class('align-end')
    iterations_result_wid.children[1].children[1].set_css('margin-bottom',
                                                          '20px')

    # align sliders and iterations_mode
    iterations_result_wid.children[1].remove_class('vbox')
    iterations_result_wid.children[1].add_class('hbox')
    iterations_result_wid.children[1].add_class('align-start')

    # set toggle button font bold
    iterations_result_wid.children[0].set_css('font-weight',
                                              toggle_button_font_weight)
    iterations_result_wid.children[1].set_css('margin-top', container_margin)

    # margin and border around container widget
    iterations_result_wid.set_css('padding', container_padding)
    iterations_result_wid.set_css('margin', container_margin)
    if border_visible:
        iterations_result_wid.set_css('border', container_border)


def update_iterations_result_options(iterations_result_wid, n_iters,
                                     image_has_gt_shape, n_points,
                                     iter_str='iter_'):
    r"""
    Function that updates the state of a given iterations_result_options widget
    if the number of iterations or the number of landmark points or the
    image_has_gt_shape flag has changed. Usage example:
        iterations_result_wid = iterations_result_options(
            n_iters=50, image_has_gt_shape=True, n_points=68)
        display(iterations_result_wid)
        format_iterations_result_options(iterations_result_wid)
        update_iterations_result_options(iterations_result_wid, n_iters=52,
                                         image_has_gt_shape=False, n_points=68)

    Parameters
    ----------
    iterations_result_wid :
        The widget generated by `iterations_result_options()` function.

    n_iters : `int`
        The number of iterations.

    image_has_gt_shape : `boolean`
        Flag that defines whether the fitted image has a ground shape attached.

    n_points : `int`
        The number of the object's  landmark points. It is required by the
        displacement dorp down menu.

    iter_str : `str`, optional
        The str that is used in the landmark groups shapes.
        E.g. if iter_str == "iter_" then the group label of iteration i has the
        form "{}{}".format(iter_str, i)
    """
    # if image_has_gt_shape flag has actually changed from the previous value
    if image_has_gt_shape != iterations_result_wid.image_has_gt_shape:
        # set the plot buttons visibility
        iterations_result_wid.children[2].children[4].visible = \
            iterations_result_wid.children[0].value and image_has_gt_shape
        iterations_result_wid.children[2].children[5].visible = \
            iterations_result_wid.children[0].value
        # store the flag
        iterations_result_wid.image_has_gt_shape = image_has_gt_shape

    # if n_points has actually changed from the previous value
    if n_points != iterations_result_wid.n_points:
        # change the contents of the displacement types
        select_menu = OrderedDict()
        select_menu['mean'] = 'mean'
        select_menu['median'] = 'median'
        select_menu['max'] = 'max'
        select_menu['min'] = 'min'
        for p in range(n_points):
            select_menu["point {}".format(p+1)] = p
        iterations_result_wid.children[2].children[5].children[1].values = \
            select_menu
        # store the number of points
        iterations_result_wid.n_points = n_points

    # if n_iters are actually different from the previous value
    if n_iters != iterations_result_wid.n_iters:
        # change the iterations_result_wid output
        iterations_result_wid.n_iters = n_iters
        iterations_result_wid.groups = _convert_iterations_to_groups(0, 0,
                                                                     iter_str)

        animation_options_wid = \
            iterations_result_wid.children[1].children[1].children[0]
        # set the iterations options state
        if n_iters == 1:
            # set sliders values and visibility
            for t in range(4):
                if t == 0:
                    # first slider
                    iterations_result_wid.children[1].children[1].children[1].\
                        value = 0
                    iterations_result_wid.children[1].children[1].children[1].\
                        max = 0
                    iterations_result_wid.children[1].children[1].children[1].\
                        visible = False
                elif t == 1:
                    # second slider
                    iterations_result_wid.children[1].children[1].children[2].\
                        value = 0
                    iterations_result_wid.children[1].children[1].children[2].\
                        max = 0
                    iterations_result_wid.children[1].children[1].children[2].\
                        visible = False
                elif t == 2:
                    # animation slider
                    animation_options_wid.selected_index = 0
                    animation_options_wid.index_max = 0
                    animation_options_wid.children[1].children[0].children[2].\
                        value = 0
                    animation_options_wid.children[1].children[0].children[2].\
                        max = 0
                    animation_options_wid.children[1].children[0].children[2].\
                        disabled = True
                    animation_options_wid.children[1].children[1].children[0].\
                        children[0].disabled = True
                    animation_options_wid.children[1].children[1].children[0].\
                        children[1].disabled = True
                    animation_options_wid.children[1].children[1].children[0].\
                        children[2].disabled = True
                else:
                    # iterations mode
                    iterations_result_wid.children[1].children[0].value = 0
                    iterations_result_wid.groups = [iter_str + "0"]
                    iterations_result_wid.children[1].children[0].\
                        disabled = True
        else:
            # set sliders max and min values
            for t in range(4):
                if t == 0:
                    # first slider
                    iterations_result_wid.children[1].children[1].children[1].\
                        value = 0
                    iterations_result_wid.children[1].children[1].children[1].\
                        max = n_iters - 1
                    iterations_result_wid.children[1].children[1].children[1].\
                        visible = False
                elif t == 1:
                    # second slider
                    iterations_result_wid.children[1].children[1].children[2].\
                        value = n_iters - 1
                    iterations_result_wid.children[1].children[1].children[2].\
                        max = n_iters - 1
                    iterations_result_wid.children[1].children[1].children[2].\
                        visible = False
                elif t == 2:
                    # animation slider
                    animation_options_wid.children[1].children[0].children[2].\
                        value = 0
                    animation_options_wid.children[1].children[0].children[2].\
                        max = n_iters - 1
                    animation_options_wid.selected_index = 0
                    animation_options_wid.index_max = n_iters - 1
                    animation_options_wid.children[1].children[0].children[2].\
                        disabled = False
                    animation_options_wid.children[1].children[1].children[0].\
                        children[0].disabled = False
                    animation_options_wid.children[1].children[1].children[0].\
                        children[1].disabled = True
                    animation_options_wid.children[1].children[1].children[0].\
                        children[2].disabled = False
                else:
                    # iterations mode
                    iterations_result_wid.children[1].children[0].value = 0
                    iterations_result_wid.groups = [iter_str + "0"]
                    iterations_result_wid.children[1].children[0].\
                        disabled = False


def animation_options(index_selection_default, plot_function=None,
                      update_function=None, index_description='Image Number',
                      index_minus_description='-', index_plus_description='+',
                      index_style='buttons', index_text_editable=True,
                      loop_default=False, interval_default=0.5,
                      toggle_show_title='Image Options',
                      toggle_show_default=True, toggle_show_visible=True):
    r"""
    Creates a widget for selecting an index and creating animations.
    Specifically, it has:
        1) An index selection widget. It can either be a slider or +/- buttons.
        2) A play toggle button.
        3) A stop toggle button.
        4) An options toggle button.
        If the options toggle is pressed, the following appear:
        5) An interval text area.
        6) A loop check box.

    The structure of the widget is the following:
        animation_options_wid.children = [toggle_button, options]
        options.children = [index_selection, animation]
        if index_style == 'buttons':
            index_selection.children = [title, minus_button, index_text,
                                        plus_button] (index_selection_buttons())
        elif index_style == 'slider':
            index_selection = index_slider (index_selection_slider())
        animation.children = [buttons, animation_options]
        buttons.children = [play_button, stop_button, play_options_button]
        animation_options.children = [interval_text, loop_checkbox]

    The returned widget saves the selected values in the following dictionary:
        animation_options_wid.selected_values
        animation_options_wid.index_style

    To fix the alignment within this widget please refer to
    `format_animation_options()` function.

    To update the state of this widget, please refer to
    `update_animation_options()` function.

    Parameters
    ----------
    index_selection_default : `dict`
        The dictionary with the default options. For example:
            index_selection_default = {'min':0,
                                       'max':100,
                                       'step':1,
                                       'index':10}

    plot_function : `function` or None, optional
        The plot function that is executed when the index value changes.
        If None, then nothing is assigned.

    update_function : `function` or None, optional
        The update function that is executed when the index value changes.
        If None, then nothing is assigned.

    index_description : `str`, optional
        The title of the index widget.

    index_minus_description : `str`, optional
        The title of the button that decreases the index.

    index_plus_description : `str`, optional
        The title of the button that increases the index.

    index_style : {``buttons`` or ``slider``}, optional
        If 'buttons', then 'index_selection_buttons()' is called.
        If 'slider', then 'index_selection_slider()' is called.

    index_text_editable : `boolean`, optional
        Flag that determines whether the index text will be editable.

    loop_default : `boolean`, optional
        If True, the animation makes loop.
        If False, the animation stops when reaching the index_max_value.

    interval_default : `float`, optional
        The interval between the animation frames.

    toggle_show_title : `str`, optional
        The title of the toggle button.

    toggle_show_default : `boolean`, optional
        Defines whether the options will be visible upon construction.

    toggle_show_visible : `boolean`, optional
        The visibility of the toggle button.
    """
    from time import sleep
    from IPython import get_ipython

    # get the kernel to use it later in order to make sure that the widgets'
    # traits changes are passed during a while-loop
    kernel = get_ipython().kernel

    # Create index widget
    if index_style == 'slider':
        index_wid = index_selection_slider(index_selection_default,
                                           plot_function=plot_function,
                                           update_function=update_function,
                                           description=index_description)
    elif index_style == 'buttons':
        index_wid = index_selection_buttons(
            index_selection_default, plot_function=plot_function,
            update_function=update_function, description=index_description,
            minus_description=index_minus_description,
            plus_description=index_plus_description, loop=loop_default,
            text_editable=index_text_editable)

    # Create other widgets
    but = ToggleButtonWidget(description=toggle_show_title,
                             value=toggle_show_default,
                             visible=toggle_show_visible)
    play_but = ToggleButtonWidget(description='Play >', value=False)
    stop_but = ToggleButtonWidget(description='Stop', value=True, disabled=True)
    play_options = ToggleButtonWidget(description='Options', value=False)
    loop = CheckboxWidget(description='Loop', value=loop_default, visible=False)
    interval = FloatTextWidget(description='Interval (sec)',
                               value=interval_default, visible=False)

    # Widget container
    tmp_options = ContainerWidget(children=[interval, loop])
    buttons = ContainerWidget(children=[play_but, stop_but, play_options])
    animation = ContainerWidget(children=[buttons, tmp_options])
    cont = ContainerWidget(children=[index_wid, animation])
    animation_options_wid = ContainerWidget(children=[but, cont])

    # Initialize variables
    animation_options_wid.selected_values = index_selection_default
    animation_options_wid.index_style = index_style

    # Play button pressed
    def play_press(name, value):
        stop_but.value = not value
        play_but.disabled = value
        play_options.disabled = value
        if value:
            play_options.value = False
    play_but.on_trait_change(play_press, 'value')

    # Stop button pressed
    def stop_press(name, value):
        play_but.value = not value
        stop_but.disabled = value
        play_options.disabled = not value
    stop_but.on_trait_change(stop_press, 'value')

    # show animation options checkbox function
    def play_options_fun(name, value):
        interval.visible = value
        loop.visible = value
    play_options.on_trait_change(play_options_fun, 'value')

    # animation function
    def play_fun(name, value):
        if loop.value:
            # loop is enabled
            i = animation_options_wid.selected_values['index']
            if i < animation_options_wid.selected_values['max']:
                i += animation_options_wid.selected_values['step']
            else:
                i = animation_options_wid.selected_values['min']
            while (i <= animation_options_wid.selected_values['max'] and
                   not stop_but.value):
                # update index value
                if index_style == 'slider':
                    index_wid.value = i
                else:
                    index_wid.children[2].value = i

                # Run IPython iteration.
                # This is the code that makes this operation non-blocking. This
                # will allow widget messages and callbacks to be processed.
                kernel.do_one_iteration()

                # update counter
                if i < animation_options_wid.selected_values['max']:
                    i += animation_options_wid.selected_values['step']
                else:
                    i = animation_options_wid.selected_values['min']

                # wait
                sleep(interval.value)
        else:
            # loop is disabled
            i = animation_options_wid.selected_values['index']
            i += animation_options_wid.selected_values['step']
            while (i <= animation_options_wid.selected_values['max'] and
                   not stop_but.value):
                # update value
                if index_style == 'slider':
                    index_wid.value = i
                else:
                    index_wid.children[2].value = i

                # Run IPython iteration.
                # This is the code that makes this operation non-blocking. This
                # will allow widget messages and callbacks to be processed.
                kernel.do_one_iteration()

                # update counter
                i += animation_options_wid.selected_values['step']

                # wait
                sleep(interval.value)
            if i > index_selection_default['max']:
                stop_but.value = True
    play_but.on_trait_change(play_fun, 'value')

    # Toggle button function
    def show_options(name, value):
        index_wid.visible = value
        buttons.visible = value
        interval.visible = False
        loop.visible = False
        if value:
            play_options.value = False
    show_options('', toggle_show_default)
    but.on_trait_change(show_options, 'value')

    return animation_options_wid


def format_animation_options(animation_options_wid, index_text_width='0.5cm',
                             container_padding='6px', container_margin='6px',
                             container_border='1px solid black',
                             toggle_button_font_weight='bold',
                             border_visible=True):
    r"""
    Function that corrects the align (style format) of a given animation_options
    widget. Usage example:
        animation_options_wid = animation_options()
        display(animation_options_wid)
        format_animation_options(animation_options_wid)

    Parameters
    ----------
    animation_options_wid :
        The widget object generated by the `animation_options()`
        function.

    index_text_width : `str`, optional
        The width of the index value text area.

    container_padding : `str`, optional
        The padding around the widget, e.g. '6px'

    container_margin : `str`, optional
        The margin around the widget, e.g. '6px'

    container_border : `str`, optional
        The border around the widget, e.g. '1px solid black'

    toggle_button_font_weight : `str`
        The font weight of the toggle button, e.g. 'bold'

    border_visible : `boolean`, optional
        Defines whether to draw the border line around the widget.
    """
    # format index widget
    format_index_selection(animation_options_wid.children[1].children[0],
                           text_width=index_text_width)

    # align play/stop button with animation options button
    animation_options_wid.children[1].children[1].children[0].remove_class(
        'vbox')
    animation_options_wid.children[1].children[1].children[0].add_class('hbox')
    animation_options_wid.children[1].children[1].add_class('align-end')

    # add margin on the right of the play button
    animation_options_wid.children[1].children[1].children[0].children[1].\
        set_css('margin-right', container_margin)

    if animation_options_wid.index_style == 'slider':
        # align animation on the right of slider
        animation_options_wid.children[1].add_class('align-end')
    else:
        # align animation and index buttons
        animation_options_wid.children[1].remove_class('vbox')
        animation_options_wid.children[1].add_class('hbox')
        animation_options_wid.children[1].add_class('align-center')
        animation_options_wid.children[1].children[0].set_css('margin-right',
                                                              '1cm')

    # set interval width
    animation_options_wid.children[1].children[1].children[1].children[0].\
        set_css('width', '20px')

    # set toggle button font bold
    animation_options_wid.children[0].set_css('font-weight',
                                              toggle_button_font_weight)

    # margin and border around container widget
    animation_options_wid.set_css('padding', container_padding)
    animation_options_wid.set_css('margin', container_margin)
    if border_visible:
        animation_options_wid.set_css('border', container_border)


def update_animation_options(animation_options_wid, index_selection_default,
                             plot_function=None, update_function=None):
    r"""
    Function that updates the state of a given animation_options widget if the
    index bounds have changed. Usage example:
        index_selection_default = {'min':0,
                                   'max':100,
                                   'step':1,
                                   'index':10}
        animation_options_wid = animation_options(index_selection_default)
        display(animation_options_wid)
        format_animation_options(animation_options_wid)
        index_selection_default = {'min':0,
                                   'max':10,
                                   'step':5,
                                   'index':5}
        update_animation_options(animation_options_wid, index_selection_default)

    Parameters
    ----------
    animation_options_wid :
        The widget object generated by either the `animation_options()`
        function.

    index_selection_default : `dict`
        The dictionary with the default options. For example:
            index_selection_default = {'min':0,
                                       'max':100,
                                       'step':1,
                                       'index':10}

    plot_function : `function` or None, optional
        The plot function that is executed when the index value changes.
        If None, then nothing is assigned.

    update_function : `function` or None, optional
        The update function that is executed when the index value changes.
        If None, then nothing is assigned.
    """
    update_index_selection(animation_options_wid.children[1].children[0],
                           index_selection_default,
                           plot_function=plot_function,
                           update_function=update_function)


def viewer_options(viewer_options_default, options_tabs, objects_names=None,
                   labels=None, plot_function=None, toggle_show_visible=True,
                   toggle_show_default=True):
    r"""
    Creates a widget with Viewer Options. Specifically, it has:
        1) A drop down menu for object selection.
        2) A tab widget with any of line, marker, numbers and feature options
        3) A toggle button that controls the visibility of all the above, i.e.
           the viewer options.

    The structure of the widgets is the following:
        viewer_options_wid.children = [toggle_button, options]
        options.children = [selection_menu, tab_options]
        tab_options.children = [line_options, marker_options,
                                numbers_options, figure_options, legend_options]

    The returned widget saves the selected values in the following dictionary:
        viewer_options_wid.selected_values

    To fix the alignment within this widget please refer to
    `format_viewer_options()` function.

    Parameters
    ----------
    viewer_options_default : list of `dict`
        A list of dictionaries with the initial selected viewer options per
        object. Example:

            lines_options = {'render_lines': True,
                             'line_width': 1,
                             'line_colour': ['b'],
                             'line_style': '-'}

            markers_options = {'render_markers':True,
                               'marker_size':20,
                               'marker_face_colour':['r'],
                               'marker_edge_colour':['k'],
                               'marker_style':'o',
                               'marker_edge_width':1}

            numbers_options = {'render_numbering': True,
                               'numbers_font_name': 'serif',
                               'numbers_font_size': 10,
                               'numbers_font_style': 'normal',
                               'numbers_font_weight': 'normal',
                               'numbers_font_colour': ['k'],
                               'numbers_horizontal_align': 'center',
                               'numbers_vertical_align': 'bottom'}

            legend_options = {'render_legend':True,
                              'legend_title':'',
                              'legend_font_name':'serif',
                              'legend_font_style':'normal',
                              'legend_font_size':10,
                              'legend_font_weight':'normal',
                              'legend_marker_scale':1.,
                              'legend_location':2,
                              'legend_bbox_to_anchor':(1.05, 1.),
                              'legend_border_axes_pad':1.,
                              'legend_n_columns':1,
                              'legend_horizontal_spacing':1.,
                              'legend_vertical_spacing':1.,
                              'legend_border':True,
                              'legend_border_padding':0.5,
                              'legend_shadow':False,
                              'legend_rounded_corners':True}

            figure_options = {'x_scale': 1.,
                              'y_scale': 1.,
                              'render_axes': True,
                              'axes_font_name': 'serif',
                              'axes_font_size': 10,
                              'axes_font_style': 'normal',
                              'axes_font_weight': 'normal',
                              'axes_x_limits': None,
                              'axes_y_limits': None}

            viewer_options_default = {'lines': lines_options,
                                      'markers': markers_options,
                                      'numbering': numbering_options,
                                      'legend': legend_options,
                                      'figure': figure_options}

    options_tabs : `list` of `str`
        List that defines the ordering of the options tabs. It can take one of
        {``lines``, ``markers``, ``numbering``, ``figure_one``, ``figure_two``,
        ``legend``}

    objects_names : `list` of `str`, optional
        A list with the names of the objects that will be used in the selection
        dropdown menu. If None, then the names will have the form ``%d``.

    plot_function : `function` or None, optional
        The plot function that is executed when a widgets' value changes.
        If None, then nothing is assigned.

    toggle_show_default : `boolean`, optional
        Defines whether the options will be visible upon construction.

    toggle_show_visible : `boolean`, optional
        The visibility of the toggle button.
    """
    # make sure that viewer_options_default is list even with one member
    if not isinstance(viewer_options_default, list):
        viewer_options_default = [viewer_options_default]

    # find number of objects
    n_objects = len(viewer_options_default)
    selection_visible = n_objects > 1

    # Create widgets
    # toggle button
    but = ToggleButtonWidget(description='Viewer Options',
                             value=toggle_show_default,
                             visible=toggle_show_visible)

    # select object drop down menu
    objects_dict = OrderedDict()
    if objects_names is None:
        for k in range(n_objects):
            objects_dict[str(k)] = k
    else:
        for k, g in enumerate(objects_names):
            objects_dict[g] = k
    selection = DropdownWidget(values=objects_dict, value=0,
                               description='Select',
                               visible=selection_visible and toggle_show_default)

    # options widgets
    options_widgets = []
    tab_titles = []
    if labels is None:
        labels = [str(j) for j in range(len(options_tabs))]
    for j, o in enumerate(options_tabs):
        if o == 'lines':
            options_widgets.append(
                line_options(viewer_options_default[0]['lines'],
                             toggle_show_visible=False,
                             toggle_show_default=True,
                             plot_function=plot_function,
                             show_checkbox_title='Render lines',
                             labels=labels[j]))
            tab_titles.append('Lines')
        elif o == 'markers':
            options_widgets.append(
                marker_options(viewer_options_default[0]['markers'],
                               toggle_show_visible=False,
                               toggle_show_default=True,
                               plot_function=plot_function,
                               show_checkbox_title='Render markers'))
            tab_titles.append('Markers')
        elif o == 'numbering':
            options_widgets.append(
                numbering_options(viewer_options_default[0]['numbering'],
                                  toggle_show_visible=False,
                                  toggle_show_default=True,
                                  plot_function=plot_function,
                                  show_checkbox_title='Render numbering'))
            tab_titles.append('Numbering')
        elif o == 'figure_one':
            options_widgets.append(
                figure_options(viewer_options_default[0]['figure'],
                               plot_function=plot_function,
                               figure_scale_bounds=(0.1, 2),
                               figure_scale_step=0.1, figure_scale_visible=True,
                               axes_visible=True, toggle_show_default=True,
                               toggle_show_visible=False))
            tab_titles.append('Figure/Axes')
        elif o == 'figure_two':
            options_widgets.append(
                figure_options_two_scales(
                    viewer_options_default[0]['figure'],
                    plot_function=plot_function, coupled_default=False,
                    figure_scales_bounds=(0.1, 2), figure_scales_step=0.1,
                    figure_scales_visible=True, axes_visible=True,
                    toggle_show_default=True, toggle_show_visible=False))
            tab_titles.append('Figure/Axes')
        elif o == 'legend':
            options_widgets.append(
                legend_options(viewer_options_default[0]['legend'],
                               toggle_show_visible=False,
                               toggle_show_default=True,
                               plot_function=plot_function,
                               show_checkbox_title='Render legend'))
            tab_titles.append('Legend')
    options = TabWidget(children=options_widgets)

    # Final widget
    all_options = ContainerWidget(children=[selection, options])
    viewer_options_wid = ContainerWidget(children=[but, all_options])

    # save tab titles and options str to widget in order to be passed to the
    # format function
    viewer_options_wid.tab_titles = tab_titles
    viewer_options_wid.options_tabs = options_tabs

    # Assign output list of dicts
    viewer_options_wid.selected_values = viewer_options_default

    # Update widgets' state
    def update_widgets(name, value):
        for i, tab in enumerate(options_tabs):
            if tab == 'lines':
                update_line_options(
                    options_widgets[i],
                    viewer_options_default[value]['lines'],
                    labels=labels[value])
            elif tab == 'markers':
                update_marker_options(
                    options_widgets[i],
                    viewer_options_default[value]['markers'])
            elif tab == 'numbering':
                update_numbering_options(
                    options_widgets[i],
                    viewer_options_default[value]['numbering'])
            elif tab == 'figure_one':
                update_figure_options(
                    options_widgets[i],
                    viewer_options_default[value]['figure'])
            elif tab == 'figure_two':
                update_figure_options_two_scales(
                    options_widgets[i],
                    viewer_options_default[value]['figure'])
            elif tab == 'legend':
                update_legend_options(
                    options_widgets[i],
                    viewer_options_default[value]['legend'])
    selection.on_trait_change(update_widgets, 'value')

    # Toggle button function
    def toggle_fun(name, value):
        selection.visible = value and selection_visible
        options.visible = value
    toggle_fun('', toggle_show_default)
    but.on_trait_change(toggle_fun, 'value')

    return viewer_options_wid


def format_viewer_options(viewer_options_wid, container_padding='6px',
                          container_margin='6px',
                          container_border='1px solid black',
                          toggle_button_font_weight='bold',
                          border_visible=False, suboptions_border_visible=True):
    r"""
    Function that corrects the align (style format) of a given
    viewer_options widget. Usage example:
        viewer_options_wid = viewer_options(default_options)
        display(viewer_options_wid)
        format_viewer_options(viewer_options_wid)

    Parameters
    ----------
    viewer_options_wid :
        The widget object generated by the `viewer_options()` function.

    container_padding : `str`, optional
        The padding around the widget, e.g. '6px'

    container_margin : `str`, optional
        The margin around the widget, e.g. '6px'

    container_border : `str`, optional
        The border around the widget, e.g. '1px solid black'

    toggle_button_font_weight : `str`
        The font weight of the toggle button, e.g. 'bold'

    border_visible : `boolean`, optional
        Defines whether to draw the border line around the widget.

    suboptions_border_visible : `boolean`, optional
        Defines whether to draw the border line around each of the sub options.
    """
    # format widgets
    for k, o in enumerate(viewer_options_wid.options_tabs):
        if o == 'lines':
            format_line_options(
                viewer_options_wid.children[1].children[1].children[k],
                suboptions_border_visible=suboptions_border_visible,
                border_visible=False)
        elif o == 'markers':
            format_marker_options(
                viewer_options_wid.children[1].children[1].children[k],
                suboptions_border_visible=suboptions_border_visible,
                border_visible=False)
        elif o == 'numbering':
            format_numbering_options(
                viewer_options_wid.children[1].children[1].children[k],
                suboptions_border_visible=suboptions_border_visible,
                border_visible=False)
        elif o == 'figure_one':
            format_figure_options(
                viewer_options_wid.children[1].children[1].children[k],
                border_visible=suboptions_border_visible)
        elif o == 'figure_two':
            format_figure_options_two_scales(
                viewer_options_wid.children[1].children[1].children[k],
                border_visible=suboptions_border_visible)
        elif o == 'legend':
            format_legend_options(
                viewer_options_wid.children[1].children[1].children[k],
                suboptions_border_visible=suboptions_border_visible,
                border_visible=False)

    # set titles
    for (k, tl) in enumerate(viewer_options_wid.tab_titles):
        viewer_options_wid.children[1].children[1].set_title(k, tl)

    # set toggle button font bold
    viewer_options_wid.children[0].set_css('font-weight',
                                           toggle_button_font_weight)

    # margin and border around container widget
    viewer_options_wid.set_css('padding', container_padding)
    viewer_options_wid.set_css('margin', container_margin)
    if border_visible:
        viewer_options_wid.set_css('border', container_border)


def update_viewer_options(viewer_options_wid, viewer_options_default,
                          labels=None):
    for k, o in enumerate(viewer_options_wid.options_tabs):
        if o == 'lines' and 'lines' in viewer_options_default:
            update_line_options(
                viewer_options_wid.children[1].children[1].children[k],
                viewer_options_default['lines'], labels=labels)
        elif o == 'markers' and viewer_options_default.has_key('markers'):
            update_marker_options(
                viewer_options_wid.children[1].children[1].children[k],
                viewer_options_default['markers'])
        elif o == 'numbering' and viewer_options_default.has_key('numbering'):
            update_numbering_options(
                viewer_options_wid.children[1].children[1].children[k],
                viewer_options_default['numbering'])
        elif o == 'figure_one' and viewer_options_default.has_key('figure'):
            update_figure_options(
                viewer_options_wid.children[1].children[1].children[k],
                viewer_options_default['figure'])
        elif o == 'figure_two' and viewer_options_default.has_key('figure'):
            update_figure_options(
                viewer_options_wid.children[1].children[1].children[k],
                viewer_options_default['figure'])
        elif o == 'legend' and viewer_options_default.has_key('legend'):
            update_legend_options(
                viewer_options_wid.children[1].children[1].children[k],
                viewer_options_default['legend'])


def plot_options(plot_options_default, plot_function=None,
                 toggle_show_visible=True, toggle_show_default=True):
    r"""
    Creates a widget with Plot Options. Specifically, it has:
        1) A drop down menu for curve selection.
        2) A text area for the legend entry.
        3) A checkbox that controls line's visibility.
        4) A checkbox that controls markers' visibility.
        5) Options for line colour, style and width.
        6) Options for markers face colour, edge colour, size, edge width and
           style.
        7) A toggle button that controls the visibility of all the above, i.e.
           the plot options.

    The structure of the widgets is the following:
        plot_options_wid.children = [toggle_button, options]
        options.children = [curve_menu, per_curve_options_wid]
        per_curve_options_wid = ContainerWidget(children=[legend_entry,
                                                          line_marker_wid])
        line_marker_wid = ContainerWidget(children=[line_widget, marker_widget])
        line_widget.children = [show_line_checkbox, line_options]
        marker_widget.children = [show_marker_checkbox, marker_options]
        line_options.children = [linestyle, linewidth, linecolour]
        marker_options.children = [markerstyle, markersize, markeredgewidth,
                                   markerfacecolour, markeredgecolour]

    The returned widget saves the selected values in the following dictionary:
        plot_options_wid.selected_options

    To fix the alignment within this widget please refer to
    `format_plot_options()` function.

    Parameters
    ----------
    plot_options_default : list of `dict`
        A list of dictionaries with the initial selected plot options per curve.
        Example:
            plot_options_1={'show_line':True,
                            'linewidth':2,
                            'linecolour':'r',
                            'linestyle':'-',
                            'show_marker':True,
                            'markersize':20,
                            'markerfacecolour':'r',
                            'markeredgecolour':'b',
                            'markerstyle':'o',
                            'markeredgewidth':1,
                            'legend_entry':'final errors'}
            plot_options_2={'show_line':False,
                            'linewidth':3,
                            'linecolour':'r',
                            'linestyle':'-',
                            'show_marker':True,
                            'markersize':60,
                            'markerfacecolour':[0.1, 0.2, 0.3],
                            'markeredgecolour':'k',
                            'markerstyle':'x',
                            'markeredgewidth':1,
                            'legend_entry':'initial errors'}
            plot_options_default = [plot_options_1, plot_options_2]

    plot_function : `function` or None, optional
        The plot function that is executed when a widgets' value changes.
        If None, then nothing is assigned.

    toggle_show_default : `boolean`, optional
        Defines whether the options will be visible upon construction.

    toggle_show_visible : `boolean`, optional
        The visibility of the toggle button.
    """
    # make sure that plot_options_default is a list even with one member
    if not isinstance(plot_options_default, list):
        plot_options_default = [plot_options_default]

    # find number of curves
    n_curves = len(plot_options_default)

    #Create widgets
    # toggle button
    but = ToggleButtonWidget(description='Plot Options',
                             value=toggle_show_default,
                             visible=toggle_show_visible)

    # select curve drop down menu
    curves_dict = OrderedDict()
    for k in range(n_curves):
        curves_dict['Curve ' + str(k)] = k
    curve_selection = DropdownWidget(values=curves_dict,
                                     value=0,
                                     description='Select curve',
                                     visible=n_curves > 1)

    # legend entry
    legend_entry = TextWidget(description='Legend entry',
                              value=plot_options_default[0]['legend_entry'])

    # show line, show markers checkboxes
    show_line = CheckboxWidget(description='Show line',
                               value=plot_options_default[0]['show_line'])
    show_marker = CheckboxWidget(description='Show markers',
                                 value=plot_options_default[0]['show_marker'])

    # linewidth, markersize
    linewidth = FloatTextWidget(description='Width',
                                value=plot_options_default[0]['linewidth'])
    markersize = IntTextWidget(description='Size',
                               value=plot_options_default[0]['markersize'])
    markeredgewidth = FloatTextWidget(
        description='Edge width',
        value=plot_options_default[0]['markeredgewidth'])

    # markerstyle
    markerstyle_dict = OrderedDict()
    markerstyle_dict['point'] = '.'
    markerstyle_dict['pixel'] = ','
    markerstyle_dict['circle'] = 'o'
    markerstyle_dict['triangle down'] = 'v'
    markerstyle_dict['triangle up'] = '^'
    markerstyle_dict['triangle left'] = '<'
    markerstyle_dict['triangle right'] = '>'
    markerstyle_dict['tri down'] = '1'
    markerstyle_dict['tri up'] = '2'
    markerstyle_dict['tri left'] = '3'
    markerstyle_dict['tri right'] = '4'
    markerstyle_dict['octagon'] = '8'
    markerstyle_dict['square'] = 's'
    markerstyle_dict['pentagon'] = 'p'
    markerstyle_dict['star'] = '*'
    markerstyle_dict['hexagon 1'] = 'h'
    markerstyle_dict['hexagon 2'] = 'H'
    markerstyle_dict['plus'] = '+'
    markerstyle_dict['x'] = 'x'
    markerstyle_dict['diamond'] = 'D'
    markerstyle_dict['thin diamond'] = 'd'
    markerstyle = DropdownWidget(values=markerstyle_dict,
                                 value=plot_options_default[0]['markerstyle'],
                                 description='Style')

    # linestyle
    linestyle_dict = OrderedDict()
    linestyle_dict['solid'] = '-'
    linestyle_dict['dashed'] = '--'
    linestyle_dict['dash-dot'] = '-.'
    linestyle_dict['dotted'] = ':'
    linestyle = DropdownWidget(values=linestyle_dict,
                               value=plot_options_default[0]['linestyle'],
                               description='Style')

    # colours
    # do not assign the plot_function here
    linecolour = colour_selection(plot_options_default[0]['linecolour'],
                                  title='Colour')
    markerfacecolour = colour_selection(plot_options_default[0]['markerfacecolour'],
                                        title='Face Colour')
    markeredgecolour = colour_selection(plot_options_default[0]['markeredgecolour'],
                                        title='Edge Colour')

    # Group widgets
    line_options = ContainerWidget(children=[linestyle, linewidth, linecolour])
    marker_options = ContainerWidget(children=[markerstyle, markersize,
                                               markeredgewidth,
                                               markerfacecolour,
                                               markeredgecolour])
    line_wid = ContainerWidget(children=[show_line, line_options])
    marker_wid = ContainerWidget(children=[show_marker, marker_options])
    line_options_options_wid = ContainerWidget(children=[line_wid, marker_wid])
    options_wid = ContainerWidget(children=[legend_entry,
                                            line_options_options_wid])
    options_and_curve_wid = ContainerWidget(children=[curve_selection,
                                                      options_wid])
    plot_options_wid = ContainerWidget(children=[but, options_and_curve_wid])

    # initialize output
    plot_options_wid.selected_options = plot_options_default

    # line options visibility
    def line_options_visible(name, value):
        linestyle.disabled = not value
        linewidth.disabled = not value
        linecolour.children[0].disabled = not value
        linecolour.children[1].children[0].disabled = not value
        linecolour.children[1].children[1].disabled = not value
        linecolour.children[1].children[2].disabled = not value
    show_line.on_trait_change(line_options_visible, 'value')

    # marker options visibility
    def marker_options_visible(name, value):
        markerstyle.disabled = not value
        markersize.disabled = not value
        markeredgewidth.disabled = not value
        markerfacecolour.children[0].disabled = not value
        markerfacecolour.children[1].children[0].disabled = not value
        markerfacecolour.children[1].children[1].disabled = not value
        markerfacecolour.children[1].children[2].disabled = not value
        markeredgecolour.children[0].disabled = not value
        markeredgecolour.children[1].children[0].disabled = not value
        markeredgecolour.children[1].children[1].disabled = not value
        markeredgecolour.children[1].children[2].disabled = not value
    show_marker.on_trait_change(marker_options_visible, 'value')

    # function that gets colour selection
    def get_colour(colour_wid):
        if colour_wid.children[0].value == 'custom':
            return [float(colour_wid.children[1].children[0].value),
                    float(colour_wid.children[1].children[1].value),
                    float(colour_wid.children[1].children[2].value)]
        else:
            return colour_wid.children[0].value

    # assign options
    def save_legend_entry(name, value):
        plot_options_wid.selected_options[curve_selection.value]['legend_entry'] = str(value)
    legend_entry.on_trait_change(save_legend_entry, 'value')

    def save_show_line(name, value):
        plot_options_wid.selected_options[curve_selection.value]['show_line'] = value
    show_line.on_trait_change(save_show_line, 'value')

    def save_show_marker(name, value):
        plot_options_wid.selected_options[curve_selection.value]['show_marker'] = value
    show_marker.on_trait_change(save_show_marker, 'value')

    def save_linewidth(name, value):
        plot_options_wid.selected_options[curve_selection.value]['linewidth'] = float(value)
    linewidth.on_trait_change(save_linewidth, 'value')

    def save_linestyle(name, value):
        plot_options_wid.selected_options[curve_selection.value]['linestyle'] = value
    linestyle.on_trait_change(save_linestyle, 'value')

    def save_markersize(name, value):
        plot_options_wid.selected_options[curve_selection.value]['markersize'] = int(value)
    markersize.on_trait_change(save_markersize, 'value')

    def save_markeredgewidth(name, value):
        plot_options_wid.selected_options[curve_selection.value]['markeredgewidth'] = float(value)
    markeredgewidth.on_trait_change(save_markeredgewidth, 'value')

    def save_markerstyle(name, value):
        plot_options_wid.selected_options[curve_selection.value]['markerstyle'] = value
    markerstyle.on_trait_change(save_markerstyle, 'value')

    def save_linecolour(name, value):
        plot_options_wid.selected_options[curve_selection.value]['linecolour'] = get_colour(linecolour)
    linecolour.children[0].on_trait_change(save_linecolour, 'value')
    linecolour.children[1].children[0].on_trait_change(save_linecolour, 'value')
    linecolour.children[1].children[1].on_trait_change(save_linecolour, 'value')
    linecolour.children[1].children[2].on_trait_change(save_linecolour, 'value')

    def save_markerfacecolour(name, value):
        plot_options_wid.selected_options[curve_selection.value]['markerfacecolour'] = get_colour(markerfacecolour)
    markerfacecolour.children[0].on_trait_change(save_markerfacecolour, 'value')
    markerfacecolour.children[1].children[0].on_trait_change(
        save_markerfacecolour, 'value')
    markerfacecolour.children[1].children[1].on_trait_change(
        save_markerfacecolour, 'value')
    markerfacecolour.children[1].children[2].on_trait_change(
        save_markerfacecolour, 'value')

    def save_markeredgecolour(name, value):
        plot_options_wid.selected_options[curve_selection.value]['markeredgecolour'] = get_colour(markeredgecolour)
    markeredgecolour.children[0].on_trait_change(save_markeredgecolour, 'value')
    markeredgecolour.children[1].children[0].on_trait_change(
        save_markeredgecolour, 'value')
    markeredgecolour.children[1].children[1].on_trait_change(
        save_markeredgecolour, 'value')
    markeredgecolour.children[1].children[2].on_trait_change(
        save_markeredgecolour, 'value')

    # set correct value to slider when drop down menu value changes
    def set_options(name, value):
        legend_entry.value = plot_options_wid.selected_options[value]['legend_entry']
        show_line.value = plot_options_wid.selected_options[value]['show_line']
        show_marker.value = plot_options_wid.selected_options[value]['show_marker']
        linewidth.value = plot_options_wid.selected_options[value]['linewidth']
        linestyle.value = plot_options_wid.selected_options[value]['linestyle']
        markersize.value = plot_options_wid.selected_options[value]['markersize']
        markerstyle.value = plot_options_wid.selected_options[value]['markerstyle']
        markeredgewidth.value = plot_options_wid.selected_options[value]['markeredgewidth']
        default_colour = plot_options_wid.selected_options[value]['linecolour']
        if not isinstance(default_colour, str):
            r_val = default_colour[0]
            g_val = default_colour[1]
            b_val = default_colour[2]
            default_colour = 'custom'
            linecolour.children[1].children[0].value = r_val
            linecolour.children[1].children[1].value = g_val
            linecolour.children[1].children[2].value = b_val
        linecolour.children[0].value = default_colour
        default_colour = plot_options_wid.selected_options[value]['markerfacecolour']
        if not isinstance(default_colour, str):
            r_val = default_colour[0]
            g_val = default_colour[1]
            b_val = default_colour[2]
            default_colour = 'custom'
            markerfacecolour.children[1].children[0].value = r_val
            markerfacecolour.children[1].children[1].value = g_val
            markerfacecolour.children[1].children[2].value = b_val
        markerfacecolour.children[0].value = default_colour
        default_colour = plot_options_wid.selected_options[value]['markeredgecolour']
        if not isinstance(default_colour, str):
            r_val = default_colour[0]
            g_val = default_colour[1]
            b_val = default_colour[2]
            default_colour = 'custom'
            markeredgecolour.children[1].children[0].value = r_val
            markeredgecolour.children[1].children[1].value = g_val
            markeredgecolour.children[1].children[2].value = b_val
        markeredgecolour.children[0].value = default_colour
    curve_selection.on_trait_change(set_options, 'value')

    # Toggle button function
    def toggle_fun(name, value):
        options_and_curve_wid.visible = value
    toggle_fun('', toggle_show_default)
    but.on_trait_change(toggle_fun, 'value')

    # assign plot_function
    if plot_function is not None:
        legend_entry.on_trait_change(plot_function, 'value')
        show_line.on_trait_change(plot_function, 'value')
        linestyle.on_trait_change(plot_function, 'value')
        linewidth.on_trait_change(plot_function, 'value')
        show_marker.on_trait_change(plot_function, 'value')
        markerstyle.on_trait_change(plot_function, 'value')
        markeredgewidth.on_trait_change(plot_function, 'value')
        markersize.on_trait_change(plot_function, 'value')
        linecolour.children[0].on_trait_change(plot_function, 'value')
        linecolour.children[1].children[0].on_trait_change(plot_function,
                                                          'value')
        linecolour.children[1].children[1].on_trait_change(plot_function,
                                                          'value')
        linecolour.children[1].children[2].on_trait_change(plot_function,
                                                          'value')
        markerfacecolour.children[0].on_trait_change(plot_function, 'value')
        markerfacecolour.children[1].children[0].on_trait_change(plot_function,
                                                                'value')
        markerfacecolour.children[1].children[1].on_trait_change(plot_function,
                                                                'value')
        markerfacecolour.children[1].children[2].on_trait_change(plot_function,
                                                                'value')
        markeredgecolour.children[0].on_trait_change(plot_function, 'value')
        markeredgecolour.children[1].children[0].on_trait_change(plot_function,
                                                                'value')
        markeredgecolour.children[1].children[1].on_trait_change(plot_function,
                                                                'value')
        markeredgecolour.children[1].children[2].on_trait_change(plot_function,
                                                                'value')

    return plot_options_wid


def format_plot_options(plot_options_wid, container_padding='6px',
                        container_margin='6px',
                        container_border='1px solid black',
                        toggle_button_font_weight='bold', border_visible=True,
                        suboptions_border_visible=True):
    r"""
    Function that corrects the align (style format) of a given figure_options
    widget. Usage example:
        plot_options_wid = plot_options()
        display(plot_options_wid)
        format_plot_options(figure_options_wid)

    Parameters
    ----------
    plot_options_wid :
        The widget object generated by the `figure_options()` function.

    container_padding : `str`, optional
        The padding around the widget, e.g. '6px'

    container_margin : `str`, optional
        The margin around the widget, e.g. '6px'

    container_border : `str`, optional
        The border around the widget, e.g. '1px solid black'

    toggle_button_font_weight : `str`
        The font weight of the toggle button, e.g. 'bold'

    border_visible : `boolean`, optional
        Defines whether to draw the border line around the widget.

    suboptions_border_visible : `boolean`, optional
        Defines whether to draw the border line around the per curve options.
    """
    # align line options with checkbox
    plot_options_wid.children[1].children[1].children[1].children[0].\
        add_class('align-end')

    # align marker options with checkbox
    plot_options_wid.children[1].children[1].children[1].children[1].\
        add_class('align-end')

    # set text boxes width
    plot_options_wid.children[1].children[1].children[1].children[0].children[1].children[1].\
        set_css('width', '1cm')
    plot_options_wid.children[1].children[1].children[1].children[1].children[1].children[1].\
        set_css('width', '1cm')
    plot_options_wid.children[1].children[1].children[1].children[1].children[1].children[2].\
        set_css('width', '1cm')

    # align line and marker options
    plot_options_wid.children[1].children[1].children[1].remove_class('vbox')
    plot_options_wid.children[1].children[1].children[1].add_class('hbox')
    if suboptions_border_visible:
        plot_options_wid.children[1].children[1].set_css('margin',
                                                         container_margin)
        plot_options_wid.children[1].children[1].set_css('border',
                                                         container_border)

    # align curve selection with line and marker options
    plot_options_wid.children[1].add_class('align-start')

    # format colour options
    format_colour_selection(
        plot_options_wid.children[1].children[1].children[1].children[0].children[1].children[2])
    format_colour_selection(
        plot_options_wid.children[1].children[1].children[1].children[1].children[1].children[3])
    format_colour_selection(
        plot_options_wid.children[1].children[1].children[1].children[1].children[1].children[4])

    # set toggle button font bold
    plot_options_wid.children[0].set_css('font-weight',
                                         toggle_button_font_weight)

    # margin and border around container widget
    plot_options_wid.set_css('padding', container_padding)
    plot_options_wid.set_css('margin', container_margin)
    if border_visible:
        plot_options_wid.set_css('border', container_border)


def save_figure_options(renderer, format_default='png', dpi_default=None,
                        orientation_default='portrait',
                        papertype_default='letter', transparent_default=False,
                        facecolour_default='w', edgecolour_default='w',
                        pad_inches_default=0.5, overwrite_default=False,
                        toggle_show_default=True, toggle_show_visible=True):
    r"""
    Creates a widget with Save Figure Options.

    The structure of the widgets is the following:
        save_figure_wid.children = [toggle_button, options, save_button]
        options.children = [path, page_setup, image_colour]
        path.children = [filename, format, papertype]
        page_setup.children = [orientation, dpi, pad_inches]
        image_colour.children = [facecolour, edgecolour, transparent]

    To fix the alignment within this widget please refer to
    `format_save_figure_options()` function.

    Parameters
    ----------
    figure_id : matplotlib.pyplot.Figure instance
        The handle of the figure to be saved.

    format_default : `str`, optional
        The default value of the format.

    dpi_default : `float`, optional
        The default value of the dpi.

    orientation_default : `str`, optional
        The default value of the orientation. 'portrait' or 'landscape'.

    papertype_default : `str`, optional
        The default value of the papertype.

    transparent_default : `boolean`, optional
        The default value of the transparency flag.

    facecolour_default : `str` or `list` of `float`, optional
        The default value of the facecolour.

    edgecolour_default : `str` or `list` of `float`, optional
        The default value of the edgecolour.

    pad_inches_default : `float`, optional
        The default value of the figure padding in inches.

    toggle_show_default : `boolean`, optional
        Defines whether the options will be visible upon construction.

    toggle_show_visible : `boolean`, optional
        The visibility of the toggle button.
    """
    from os import getcwd
    from os.path import join, splitext

    # create widgets
    but = ToggleButtonWidget(description='Save Figure',
                             value=toggle_show_default,
                             visible=toggle_show_visible)
    format_dict = OrderedDict()
    format_dict['png'] = 'png'
    format_dict['jpg'] = 'jpg'
    format_dict['pdf'] = 'pdf'
    format_dict['eps'] = 'eps'
    format_dict['postscript'] = 'ps'
    format_dict['svg'] = 'svg'
    format_wid = SelectWidget(values=format_dict, value=format_default,
                              description='Format')

    def papertype_visibility(name, value):
        papertype_wid.disabled = not value == 'ps'
    format_wid.on_trait_change(papertype_visibility, 'value')

    def set_extension(name, value):
        fileName, fileExtension = splitext(filename.value)
        filename.value = fileName + '.' + value
    format_wid.on_trait_change(set_extension, 'value')
    if dpi_default is None:
        dpi_default = 0
    dpi_wid = FloatTextWidget(description='DPI', value=dpi_default)
    orientation_dict = OrderedDict()
    orientation_dict['portrait'] = 'portrait'
    orientation_dict['landscape'] = 'landscape'
    orientation_wid = DropdownWidget(values=orientation_dict,
                                     value=orientation_default,
                                     description='Orientation')
    papertype_dict = OrderedDict()
    papertype_dict['letter'] = 'letter'
    papertype_dict['legal'] = 'legal'
    papertype_dict['executive'] = 'executive'
    papertype_dict['ledger'] = 'ledger'
    papertype_dict['a0'] = 'a0'
    papertype_dict['a1'] = 'a1'
    papertype_dict['a2'] = 'a2'
    papertype_dict['a3'] = 'a3'
    papertype_dict['a4'] = 'a4'
    papertype_dict['a5'] = 'a5'
    papertype_dict['a6'] = 'a6'
    papertype_dict['a7'] = 'a7'
    papertype_dict['a8'] = 'a8'
    papertype_dict['a9'] = 'a9'
    papertype_dict['a10'] = 'a10'
    papertype_dict['b0'] = 'b0'
    papertype_dict['b1'] = 'b1'
    papertype_dict['b2'] = 'b2'
    papertype_dict['b3'] = 'b3'
    papertype_dict['b4'] = 'b4'
    papertype_dict['b5'] = 'b5'
    papertype_dict['b6'] = 'b6'
    papertype_dict['b7'] = 'b7'
    papertype_dict['b8'] = 'b8'
    papertype_dict['b9'] = 'b9'
    papertype_dict['b10'] = 'b10'
    papertype_wid = DropdownWidget(values=papertype_dict,
                                   value=papertype_default,
                                   description='Paper type',
                                   disabled=not format_default == 'ps')
    transparent_wid = CheckboxWidget(description='Transparent',
                                     value=transparent_default)
    facecolour_wid = colour_selection([facecolour_default], title='Face colour')
    edgecolour_wid = colour_selection([edgecolour_default], title='Edge colour')
    pad_inches_wid = FloatTextWidget(description='Pad (inch)',
                                     value=pad_inches_default)
    filename = TextWidget(description='Path',
                          value=join(getcwd(), 'Untitled.' + format_default))
    overwrite = CheckboxWidget(description='Overwrite if file exists',
                               value=overwrite_default)
    error_str = LatexWidget(value="")
    save_but = ButtonWidget(description='Save')

    # create final widget
    path_wid = ContainerWidget(children=[filename, format_wid, overwrite,
                                         papertype_wid])
    page_wid = ContainerWidget(children=[orientation_wid, dpi_wid,
                                         pad_inches_wid])
    colour_wid = ContainerWidget(children=[facecolour_wid, edgecolour_wid,
                                           transparent_wid])
    options_wid = TabWidget(children=[path_wid, page_wid, colour_wid])
    save_wid = ContainerWidget(children=[save_but, error_str])
    save_figure_wid = ContainerWidget(children=[but, options_wid, save_wid])

    # Assign renderer
    save_figure_wid.renderer = [renderer]

    # save function
    def save_function(name):
        # set save button state
        error_str.value = ''
        save_but.description = 'Saving...'
        save_but.disabled = True

        # save figure
        selected_dpi = dpi_wid.value
        if dpi_wid.value == 0:
            selected_dpi = None
        try:
            save_figure_wid.renderer[0].save_figure(
                filename=filename.value, dpi=selected_dpi,
                face_colour=facecolour_wid.selected_values['colour'][0],
                edge_colour=edgecolour_wid.selected_values['colour'][0],
                orientation=orientation_wid.value,
                paper_type=papertype_wid.value, format=format_wid.value,
                transparent=transparent_wid.value,
                pad_inches=pad_inches_wid.value, overwrite=overwrite.value)
            error_str.value = ''
        except ValueError as e:
            if (e.message == 'File already exists. Please set the overwrite '
                             'kwarg if you wish to overwrite the file.'):
                error_str.value = 'File exists! Select overwrite to replace.'
            else:
                error_str.value = e.message

        # set save button state
        save_but.description = 'Save'
        save_but.disabled = False
    save_but.on_click(save_function)

    # Toggle button function
    def show_options(name, value):
        options_wid.visible = value
        save_but.visible = value
    show_options('', toggle_show_default)
    but.on_trait_change(show_options, 'value')

    return save_figure_wid


def format_save_figure_options(save_figure_wid, container_padding='6px',
                               container_margin='6px',
                               container_border='1px solid black',
                               toggle_button_font_weight='bold',
                               tab_top_margin='0.3cm',
                               border_visible=True):
    r"""
    Function that corrects the align (style format) of a given
    save_figure_options widget. Usage example:
        save_figure_wid = save_figure_options()
        display(save_figure_wid)
        format_save_figure_options(save_figure_wid)

    Parameters
    ----------
    save_figure_wid :
        The widget object generated by the `save_figure_options()` function.

    container_padding : `str`, optional
        The padding around the widget, e.g. '6px'

    container_margin : `str`, optional
        The margin around the widget, e.g. '6px'

    tab_top_margin : `str`, optional
        The margin around the tab options' widget, e.g. '0.3cm'

    container_border : `str`, optional
        The border around the widget, e.g. '1px solid black'

    toggle_button_font_weight : `str`
        The font weight of the toggle button, e.g. 'bold'

    border_visible : `boolean`, optional
        Defines whether to draw the border line around the widget.
    """
    # add margin on top of tabs widget
    save_figure_wid.children[1].set_css('margin-top', tab_top_margin)

    # align path options to the right
    save_figure_wid.children[1].children[0].add_class('align-end')

    # align save button and error message horizontally
    save_figure_wid.children[2].remove_class('vbox')
    save_figure_wid.children[2].add_class('hbox')
    save_figure_wid.children[2].children[1].set_css({'margin-left': '0.5cm',
                                                     'background-color': 'red'})

    # set final tab titles
    tab_titles = ['Path', 'Page setup', 'Image colour']
    for (k, tl) in enumerate(tab_titles):
        save_figure_wid.children[1].set_title(k, tl)

    format_colour_selection(save_figure_wid.children[1].children[2].children[0])
    format_colour_selection(save_figure_wid.children[1].children[2].children[1])
    save_figure_wid.children[1].children[0].children[0].set_css('width', '6cm')
    save_figure_wid.children[1].children[0].children[1].set_css('width', '6cm')

    # set toggle button font bold
    save_figure_wid.children[0].set_css('font-weight',
                                        toggle_button_font_weight)

    # margin and border around container widget
    save_figure_wid.set_css('padding', container_padding)
    save_figure_wid.set_css('margin', container_margin)
    if border_visible:
        save_figure_wid.set_css('border', container_border)


def features_options(toggle_show_default=True, toggle_show_visible=True):
    r"""
    Creates a widget with Features Options.

    The structure of the widgets is the following:
        features_options_wid.children = [toggle_button, tab_options]
        tab_options.children = [features_radiobuttons, per_feature_options,
                                preview]
        per_feature_options.children = [hog_options, igo_options, lbp_options,
                                        daisy_options, no_options]
        preview.children = [input_size_text, lenna_image, output_size_text,
                            elapsed_time]

    To fix the alignment within this widget please refer to
    `format_features_options()` function.

    Parameters
    ----------
    toggle_show_default : `boolean`, optional
        Defines whether the options will be visible upon construction.

    toggle_show_visible : `boolean`, optional
        The visibility of the toggle button.
    """
    # import features methods and time
    import time
    from menpo.feature.features import hog, lbp, igo, es, daisy, gradient, no_op
    from menpo.image import Image
    import menpo.io as mio
    from menpo.visualize.image import glyph

    # Toggle button that controls options' visibility
    but = ToggleButtonWidget(description='Features Options',
                             value=toggle_show_default,
                             visible=toggle_show_visible)

    # feature type
    tmp = OrderedDict()
    tmp['HOG'] = hog
    tmp['IGO'] = igo
    tmp['ES'] = es
    tmp['Daisy'] = daisy
    tmp['LBP'] = lbp
    tmp['Gradient'] = gradient
    tmp['None'] = no_op
    feature = RadioButtonsWidget(value=no_op, values=tmp,
                                 description='Feature type:')

    # feature-related options
    hog_options_wid = hog_options(toggle_show_default=True,
                                  toggle_show_visible=False)
    igo_options_wid = igo_options(toggle_show_default=True,
                                  toggle_show_visible=False)
    lbp_options_wid = lbp_options(toggle_show_default=True,
                                  toggle_show_visible=False)
    daisy_options_wid = daisy_options(toggle_show_default=True,
                                      toggle_show_visible=False)
    no_options_wid = LatexWidget(value='No options available.')

    # load and rescale preview image (lenna)
    image = mio.import_builtin_asset.lenna_png()
    image.crop_to_landmarks_proportion_inplace(0.18)
    image = image.as_greyscale()

    # per feature options widget
    per_feature_options = ContainerWidget(children=[hog_options_wid,
                                                    igo_options_wid,
                                                    lbp_options_wid,
                                                    daisy_options_wid,
                                                    no_options_wid])

    # preview tab widget
    preview_img = ImageWidget(value=_convert_image_to_bytes(image),
                              visible=False)
    preview_input = LatexWidget(value="Input: {}W x {}H x {}C".format(
        image.width, image.height, image.n_channels), visible=False)
    preview_output = LatexWidget(value="")
    preview_time = LatexWidget(value="")
    preview = ContainerWidget(children=[preview_img, preview_input,
                                        preview_output, preview_time])

    # options tab widget
    all_options = TabWidget(children=[feature, per_feature_options, preview])

    # Widget container
    features_options_wid = ContainerWidget(children=[but, all_options])

    # Initialize output dictionary
    options = {}
    features_options_wid.function = partial(no_op, **options)
    features_options_wid.features_function = no_op
    features_options_wid.features_options = options

    # options visibility
    def per_feature_options_visibility(name, value):
        if value == hog:
            igo_options_wid.visible = False
            lbp_options_wid.visible = False
            daisy_options_wid.visible = False
            no_options_wid.visible = False
            hog_options_wid.visible = True
        elif value == igo:
            hog_options_wid.visible = False
            lbp_options_wid.visible = False
            daisy_options_wid.visible = False
            no_options_wid.visible = False
            igo_options_wid.visible = True
        elif value == lbp:
            hog_options_wid.visible = False
            igo_options_wid.visible = False
            daisy_options_wid.visible = False
            no_options_wid.visible = False
            lbp_options_wid.visible = True
        elif value == daisy:
            hog_options_wid.visible = False
            igo_options_wid.visible = False
            lbp_options_wid.visible = False
            no_options_wid.visible = False
            daisy_options_wid.visible = True
        else:
            hog_options_wid.visible = False
            igo_options_wid.visible = False
            lbp_options_wid.visible = False
            daisy_options_wid.visible = False
            no_options_wid.visible = True
            for name, f in tmp.iteritems():
                if f == value:
                    no_options_wid.value = "{}: No available " \
                                           "options.".format(name)
    feature.on_trait_change(per_feature_options_visibility, 'value')
    per_feature_options_visibility('', no_op)

    # get function
    def get_function(name, value):
        # get options
        if feature.value == hog:
            opts = hog_options_wid.options
        elif feature.value == igo:
            opts = igo_options_wid.options
        elif feature.value == lbp:
            opts = lbp_options_wid.options
        elif feature.value == daisy:
            opts = daisy_options_wid.options
        else:
            opts = {}
        # get features function closure
        func = partial(feature.value, **opts)
        # store function
        features_options_wid.function = func
        features_options_wid.features_function = value
        features_options_wid.features_options = opts
    feature.on_trait_change(get_function, 'value')
    all_options.on_trait_change(get_function, 'selected_index')

    # preview function
    def preview_function(name, old_value, value):
        if value == 2:
            # extracting features message
            for name, f in tmp.iteritems():
                if f == features_options_wid.function.func:
                    val1 = name
            preview_output.value = "Previewing {} features...".format(val1)
            preview_time.value = ""
            # extract feature and time it
            t = time.time()
            feat_image = features_options_wid.function(image)
            t = time.time() - t
            # store feature image shape and n_channels
            val2 = feat_image.width
            val3 = feat_image.height
            val4 = feat_image.n_channels
            # compute sum of feature image and normalize its pixels in range (0, 1)
            # because it is required by as_PILImage
            feat_image = glyph(feat_image, vectors_block_size=1, use_negative=False)
            #feat_image = np.sum(feat_image.pixels, axis=2)
            feat_image = feat_image.pixels
            feat_image -= np.min(feat_image)
            feat_image /= np.max(feat_image)
            feat_image = Image(feat_image)
            # update preview
            preview_img.value = _convert_image_to_bytes(feat_image)
            preview_input.visible = True
            preview_img.visible = True
            # set info
            preview_output.value = "{}: {}W x {}H x {}C".format(val1, val2,
                                                                val3, val4)
            preview_time.value = "{0:.2f} secs elapsed".format(t)
        if old_value == 2:
            preview_input.visible = False
            preview_img.visible = False
    all_options.on_trait_change(preview_function, 'selected_index')

    # Toggle button function
    def toggle_options(name, value):
        all_options.visible = value
    but.on_trait_change(toggle_options, 'value')

    return features_options_wid


def format_features_options(features_options_wid, container_padding='6px',
                            container_margin='6px',
                            container_border='1px solid black',
                            toggle_button_font_weight='bold',
                            border_visible=True):
    r"""
    Function that corrects the align (style format) of a given features_options
    widget. Usage example:
        features_options_wid = features_options()
        display(features_options_wid)
        format_features_options(features_options_wid)

    Parameters
    ----------
    features_options_wid :
        The widget object generated by the `features_options()` function.

    container_padding : `str`, optional
        The padding around the widget, e.g. '6px'

    container_margin : `str`, optional
        The margin around the widget, e.g. '6px'

    tab_top_margin : `str`, optional
        The margin around the tab options' widget, e.g. '0.3cm'

    container_border : `str`, optional
        The border around the widget, e.g. '1px solid black'

    toggle_button_font_weight : `str`
        The font weight of the toggle button, e.g. 'bold'

    border_visible : `boolean`, optional
        Defines whether to draw the border line around the widget.
    """
    # format per feature options
    format_hog_options(features_options_wid.children[1].children[1].children[0],
                       border_visible=False)
    format_igo_options(features_options_wid.children[1].children[1].children[1],
                       border_visible=False)
    format_lbp_options(features_options_wid.children[1].children[1].children[2],
                       border_visible=False)
    format_daisy_options(features_options_wid.children[1].children[1].children[3],
                         border_visible=False)

    # set final tab titles
    tab_titles = ['Feature', 'Options', 'Preview']
    for (k, tl) in enumerate(tab_titles):
        features_options_wid.children[1].set_title(k, tl)

    # set margin above tab widget
    features_options_wid.children[1].set_css('margin', '10px')

    # set toggle button font bold
    features_options_wid.children[0].set_css('font-weight',
                                             toggle_button_font_weight)

    # margin and border around container widget
    features_options_wid.set_css('padding', container_padding)
    features_options_wid.set_css('margin', container_margin)
    if border_visible:
        features_options_wid.set_css('border', container_border)


def _compare_groups_and_labels(groups1, labels1, groups2, labels2):
    r"""
    Function that compares two sets of landmarks groups and labels and returns
    Trues if they are identical else False.

    Parameters
    ----------
    group1 : `list` of `str`
        The first list of landmark groups.

    labels1 : `list` of `list` of `str`
        The first list of lists of each landmark group's labels.

    group2 : `list` of `str`
        The second list of landmark groups.

    labels2 : `list` of `list` of `str`
        The second list of lists of each landmark group's labels.
    """
    # function that compares two lists without taking into account the order
    def comp_lists(l1, l2):
        return len(l1) == len(l2) and \
               np.all([g1 == g2 for g1, g2 in zip(l1, l2)])

    # comparison of the given groups
    groups_same = comp_lists(groups1, groups2)

    # if groups are the same, compare the labels
    if groups_same:
        return len(labels1) == len(labels2) and \
               np.all([comp_lists(g1, g2) for g1, g2 in zip(labels1, labels2)])
    else:
        return False


def _convert_iterations_to_groups(from_iter, to_iter, iter_str):
    r"""
    Function that generates a list of group labels given the range bounds and
    the str to be used.
    """
    return ["{}{}".format(iter_str, i) for i in range(from_iter, to_iter+1)]

"""Let users enter height in centimeters or feet and inches."""
import math

import streamlit as st


def feet_inches_to_cm(feet, inches):
    feet, inches = float(feet), float(inches)
    if not (math.isfinite(feet) and math.isfinite(inches) and feet.is_integer()
            and 0 <= inches < 12):
        raise ValueError('Enter whole feet and inches from 0 to less than 12.')
    height = (feet * 12 + inches) * 2.54
    if not 50 <= height <= 250:
        raise ValueError('Enter a height between 50 and 250 cm (about 1 ft 8 in to 8 ft 2 in).')
    return height


def _sync_display():
    height = st.session_state.get('capture_height_cm', 175.0)
    feet, inches = divmod(height / 2.54, 12)
    inches = round(inches, 1)
    if inches >= 12:
        feet, inches = feet + 1, 0.0
    st.session_state.update(capture_height_metric=float(height), capture_height_feet=int(feet),
                            capture_height_inches=float(inches))


def _height_changed(invalidate):
    try:
        height = (st.session_state['capture_height_metric']
                  if st.session_state['capture_height_unit'] == 'Centimeters'
                  else feet_inches_to_cm(st.session_state['capture_height_feet'],
                                         st.session_state['capture_height_inches']))
        st.session_state['capture_height_cm'] = height
    except ValueError:
        pass
    invalidate()


def render_height_input(invalidate):
    st.session_state.setdefault('capture_height_cm', 175.0)
    unit = st.selectbox('Height unit', ['Centimeters', 'Feet & inches'], key='capture_height_unit',
                        on_change=_sync_display)
    active_keys = (['capture_height_metric'] if unit == 'Centimeters'
                   else ['capture_height_feet', 'capture_height_inches'])
    if any(key not in st.session_state for key in active_keys):
        _sync_display()
    help_text = 'Enter your measured height. SI uses this height divided by a waveform delay.'
    if unit == 'Centimeters':
        st.number_input('Height (cm), used to calculate SI', min_value=50.0, max_value=250.0,
                        step=1.0, key='capture_height_metric', on_change=_height_changed,
                        args=(invalidate,), help=help_text)
    else:
        feet, inches = st.columns(2)
        feet.number_input('Feet', min_value=1, max_value=8, step=1, key='capture_height_feet',
                           on_change=_height_changed, args=(invalidate,), help=help_text)
        inches.number_input('Inches', min_value=0.0, max_value=11.9, step=.1,
                             key='capture_height_inches', on_change=_height_changed, args=(invalidate,))
        try:
            converted = feet_inches_to_cm(st.session_state['capture_height_feet'], st.session_state['capture_height_inches'])
        except ValueError as error:
            st.error(str(error))
            return False
        st.caption(f'{st.session_state["capture_height_feet"]} ft {st.session_state["capture_height_inches"]:g} in ≈ {converted:.1f} cm. Height is used for SI.')
    return True

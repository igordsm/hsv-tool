import asyncio
from js import window, document, Uint8Array
import cv2
import io
from pyodide import create_proxy
import numpy as np
import base64


def save_and_show_image(img_cv2, el_id):
    _, img_png_data = cv2.imencode('.png', img_cv2)
    img_png_data = b'data:image/png; base64, ' + base64.b64encode(img_png_data)
    document.getElementById(el_id).src = img_png_data.decode('ascii')

class UI:
    def __init__(self) -> None:
        self.range_controls = {
                id: document.getElementById(id) for id in
                ['Hmin', 'Hmax', 'Smin', 'Smax', 'Vmin', 'Vmax']
                }
        apply_filters = create_proxy(self._apply_filters)
        for r in self.range_controls.values():
             r.addEventListener('change', apply_filters)

        self.filter_values_div = document.getElementById('filterValuesBox')

        self.image_hsv = None
        load_image = create_proxy(self._load_image)
        self.file_box = document.getElementById('fileBox')
        self.file_box.addEventListener('change', load_image)

        self.toggle_enabled_controls()

        
        document.getElementById('noImageSelected').addEventListener('click', create_proxy(self.no_image_callback))

    def no_image_callback(self, evt):
        self.file_box.click()
        document.getElementById('imageFilterPreview').classList.toggle('hide')
        document.getElementById('noImageSelected').classList.toggle('hide')


    def toggle_enabled_controls(self):
        for r in self.range_controls.values():
            r.disabled = self.image_hsv is None


    def _apply_filters(self, evt):
        minh_value = int(self.range_controls['Hmin'].value)
        mins_value = int(self.range_controls['Smin'].value)
        minv_value = int(self.range_controls['Vmin'].value)
        
        maxh_value = int(self.range_controls['Hmax'].value)
        maxs_value = int(self.range_controls['Smax'].value)
        maxv_value = int(self.range_controls['Vmax'].value)

        # show_filter_values()
        self.filter_values_div.innerText = f'''
minValue = ({minh_value//2}, {mins_value}, {minv_value})
maxValue = ({maxh_value//2}, {maxs_value}, {maxv_value})
'''
        if self.image_hsv is not None:
            mask = cv2.inRange(self.image_hsv, (minh_value//2, mins_value, minv_value), (maxh_value//2, maxs_value, maxv_value))
            save_and_show_image(mask, 'outImg')

    async def _load_image(self, evt):
        file_list = self.file_box.files
        first_item = file_list.item(0)
        array_buf = Uint8Array.new(await first_item.arrayBuffer())
        bytes_list = bytearray(array_buf)
        my_bytes = io.BytesIO(bytes_list)
        
        image_bgr = cv2.imdecode(np.frombuffer(my_bytes.read(), np.uint8), 1)
        self.image_hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)
        
        self.toggle_enabled_controls()
        save_and_show_image(image_bgr, 'inImg') 

        self._apply_filters(None)


ui = UI()


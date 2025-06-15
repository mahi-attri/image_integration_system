from flask import Flask, render_template, request, send_file
from PIL import Image
import cv2
import numpy as np
import os

class WorkingSolution:
    def __init__(self, person_path="person_image.png", bg_path="bg_image.jpg"):
        self.output_dir = "outputs"
        os.makedirs(self.output_dir, exist_ok=True)
        self.person_path = person_path
        self.bg_path = bg_path

    def load_images(self):
        person_bgr = cv2.imread(self.person_path)
        bg_bgr = cv2.imread(self.bg_path)
        if person_bgr is None or bg_bgr is None:
            raise FileNotFoundError("Image loading failed.")
        return person_bgr, bg_bgr

    def create_grabcut_mask(self, img):
        mask = np.zeros(img.shape[:2], np.uint8)
        height, width = img.shape[:2]
        rect = (int(width * 0.05), int(height * 0.0), int(width * 0.9), int(height * 1.0))
        bgdModel = np.zeros((1, 65), np.float64)
        fgdModel = np.zeros((1, 65), np.float64)
        cv2.grabCut(img, mask, rect, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_RECT)
        mask_binary = np.where((mask == 2) | (mask == 0), 0, 1).astype(np.float32)
        feathered_mask = cv2.GaussianBlur(mask_binary, (5, 5), 0)
        final_mask = np.where(np.arange(height)[:, None] < 20, feathered_mask, mask_binary)
        return final_mask

    def resize_and_place(self, person_img, person_mask, bg_shape):
        bg_h, bg_w = bg_shape[:2]
        target_height = int(bg_h * 0.9)
        scale = target_height / person_img.shape[0]
        target_width = int(person_img.shape[1] * scale)
        person_resized = cv2.resize(person_img, (target_width, target_height), interpolation=cv2.INTER_LINEAR)
        mask_resized = cv2.resize(person_mask, (target_width, target_height), interpolation=cv2.INTER_LINEAR)
        pos_x = (bg_w - target_width) // 2
        pos_y = int(bg_h - target_height * 0.95)
        return person_resized, mask_resized, (pos_x, pos_y)

    def create_simple_shadow(self, mask, bg_shape, pos):
        bg_h, bg_w = bg_shape[:2]
        sh_x, sh_y = pos
        mask_h, mask_w = mask.shape[:2]
        shadow = np.zeros((bg_h, bg_w), dtype=np.float32)
        contact_mask = mask[int(mask_h * 0.85):, :]
        contact_mask_resized = cv2.resize(contact_mask, (mask_w, int(mask_h * 0.1)))
        contact_mask_resized = cv2.GaussianBlur(contact_mask_resized, (31, 15), 0)
        contact_mask_resized *= 0.7
        shadow_y_start = sh_y + int(mask_h * 0.9)
        shadow_y_end = min(shadow_y_start + contact_mask_resized.shape[0], bg_h)
        shadow[shadow_y_start:shadow_y_end, sh_x:sh_x + mask_w] = contact_mask_resized[:shadow_y_end - shadow_y_start, :]
        return cv2.GaussianBlur(shadow, (31, 15), 0)

    def direct_composite(self, bg_img, person_img, person_mask, shadow_mask, pos):
        result = bg_img.copy().astype(np.float32)
        for c in range(3):
            result[:, :, c] *= (1.0 - shadow_mask * 0.5)
        x, y = pos
        ph, pw = person_img.shape[:2]
        end_x = min(x + pw, result.shape[1])
        end_y = min(y + ph, result.shape[0])
        actual_w = end_x - x
        actual_h = end_y - y
        roi_bg = result[y:end_y, x:end_x]
        roi_person = person_img[:actual_h, :actual_w].astype(np.float32)
        roi_mask = person_mask[:actual_h, :actual_w]
        mask_3ch = np.stack([roi_mask] * 3, axis=-1)
        blended = roi_person * mask_3ch + roi_bg * (1 - mask_3ch)
        result[y:end_y, x:end_x] = blended
        return np.clip(result, 0, 255).astype(np.uint8)

    def process(self, output_file="WORKING_SOLUTION_FINAL_POLISHED.jpg"):
        person_bgr, bg_bgr = self.load_images()
        grabcut_mask = self.create_grabcut_mask(person_bgr)
        person_rgb = cv2.cvtColor(person_bgr, cv2.COLOR_BGR2RGB)
        bg_rgb = cv2.cvtColor(bg_bgr, cv2.COLOR_BGR2RGB)
        person_resized, mask_resized, pos = self.resize_and_place(person_rgb, grabcut_mask, bg_rgb.shape)
        shadow_mask = self.create_simple_shadow(mask_resized, bg_rgb.shape, pos)
        final_img = self.direct_composite(bg_rgb, person_resized, mask_resized, shadow_mask, pos)
        out_path = os.path.join(self.output_dir, output_file)
        Image.fromarray(final_img).save(out_path)
        print(f"Final image saved at: {out_path}")

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/process', methods=['POST'])
def process():
    file = request.files['person_image']
    file.save("person_image.png")
    bg_file = request.files['bg_image']
    bg_file.save("bg_image.jpg")
    solution = WorkingSolution("person_image.png", "bg_image.jpg")
    solution.process()
    return send_file("outputs/WORKING_SOLUTION_FINAL_POLISHED.jpg", mimetype='image/jpeg')

if __name__ == '__main__':
    app.run(debug=True)
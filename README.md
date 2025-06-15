
# AI Scene Integration Studio

**AI Scene Integration Studio** is a web application that allows users to seamlessly insert a person into a background scene using computer vision techniques for foreground extraction, lighting-aware positioning, shadow simulation and alpha blending. The system produces a photorealistic final image with intuitive drag-and-drop interaction.

## 📁 Project Structure

```
├── app.py                              # Flask backend logic
├── templates/                          # HTML frontend templates
│   ├── index.html
│   ├── result.html
│   └── update.html
├── outputs/                            # Final output image and intermediate files
│   └── WORKING_SOLUTION_FINAL_POLISHED.jpg
├── person_image.png                    # Uploaded person image (runtime)
├── bg_image.jpg                        # Uploaded background image (runtime)
```


## 🌐 Live Demo

👉 [Deployed App on Render](https://image-integration-system.onrender.com)

## 📸 Example

### Input Images
<table>
  <tr>
    <td><strong>Person Image</strong></td>
    <td><strong>Background Image</strong></td>
  </tr>
  <tr>
    <td><img src="person_image.png" alt="Person" width="300"/></td>
    <td><img src="bg_image.jpg" alt="Background" width="300"/></td>
  </tr>
</table>

### Output Image

| Final Composite |
|------------------|
| ![Result](outputs/WORKING_SOLUTION_FINAL_POLISHED.jpg) |


## 🔧 Features

- Drag-and-drop upload interface: person and background images.
- Automatic background removal using OpenCV's GrabCut.
- Soft mask blending and resizing of person to fit scene context.
- Shadow generation beneath the subject for realism.
- Final photorealistic output saved and displayed for download.

## ⚙️ Requirements

- Python 3.x  
- Flask  
- OpenCV (cv2)  
- Pillow (PIL)  

Install with:

```bash
pip install flask opencv-python pillow
```

## 🚀 How to Run Locally

```bash
python app.py
```

Then open your browser and go to: [http://127.0.0.1:5000](http://127.0.0.1:5000)

## 🖼 Output

The processed image is saved as:

```
outputs/WORKING_SOLUTION_FINAL_POLISHED.jpg
```



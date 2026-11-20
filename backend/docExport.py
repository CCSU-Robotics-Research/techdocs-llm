import re
from io import BytesIO
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile




#Compress HTML export and keyframes into a zip file
def html_export(output_dir: Path) -> bytes:
    html_file = sorted(output_dir.glob("*.html"))

#Error handling
    if not html_file:
        raise FileNotFoundError("Generated HTML doc not found in directory")


    html_path = html_file[0]
    html = html_path.read_text(encoding="utf-8")


    #Find all keyframe files in the HTML
    image_names = sorted(set(re.findall(
        r"""<img\b[^>]*\bsrc=["'](frame_\d+\.jpg)["']""",
        html,
        flags=re.IGNORECASE,
    )))

    #Check if all keyframe files exist in the output directory
    image_paths = [output_dir / name for name in image_names]

    for image_path in image_paths:
        if not image_path.exists():
            raise FileNotFoundError(f"Keyframe source image {image_path} not found in directory")

    #Build zip file in memory to avoid duplicate temp files override popup
    zip_buffer = BytesIO()

    with ZipFile(zip_buffer, mode="w", compression=ZIP_DEFLATED) as zip_file:
        #Add HTML file to zip
        zip_file.write(html_path, arcname=html_path.name)

        #Add keyframe files to zip
        for image_path in image_paths:
            zip_file.write(image_path, arcname=image_path.name)

    #Return the compressed zip file as bytes
    return zip_buffer.getvalue()
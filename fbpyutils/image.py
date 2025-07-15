import os
import io
import logging
from typing import Union, Optional, Tuple
from PIL import Image, ImageEnhance, ImageFilter
from PIL.ExifTags import TAGS, GPSTAGS
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

def _load_image_from_source(image_source: Union[str, bytes]) -> Tuple[Image.Image, str, int]:
    """
    Load image from file path or bytes and return image object with metadata.
    
    Args:
        image_source: Path to image file (str) or image bytes (bytes)
        
    Returns:
        Tuple[Image.Image, str, int]: Image object, filename, and file size
    """
    try:
        if isinstance(image_source, str):
            if not os.path.exists(image_source):
                raise ValueError("File not found")
            
            file_stats = os.stat(image_source)
            file_size = file_stats.st_size
            filename = os.path.basename(image_source)
            img = Image.open(image_source)
            
        elif isinstance(image_source, bytes):
            if not image_source:
                raise ValueError("Empty byte array provided")
            
            file_size = len(image_source)
            filename = "image_from_bytes"
            img = Image.open(io.BytesIO(image_source))
            
        else:
            raise ValueError("Invalid input type. Expected str (file path) or bytes (image data)")
            
        return img, filename, file_size
        
    except Exception as e:
        raise ValueError(f"Error loading image: {str(e)}")

def get_image_info(image_source: Union[str, bytes]) -> dict:
    """
    Extract detailed information from an image including EXIF metadata and geolocation.
    
    Args:
        image_source: Path to image file (str) or image bytes (bytes)
        
    Returns:
        dict: Dictionary with image information
    """
    try:
        # Load image using utility function
        img, filename, file_size = _load_image_from_source(image_source)
        
        with img:
            # Basic image information
            info = {
                "filename": filename,
                "file_size": file_size,
                "file_size_mb": round(file_size / (1024 * 1024), 2),
                "format": img.format,
                "mode": img.mode,
                "width": img.size[0],
                "height": img.size[1],
                "resolution": f"{img.size[0]}x{img.size[1]}",
                "has_transparency": img.mode in ('RGBA', 'LA') or 'transparency' in img.info,
                "color_channels": len(img.getbands()) if hasattr(img, 'getbands') else None,
                
                # EXIF information
                "camera_make": "",
                "camera_model": "",
                "datetime_taken": "",
                "orientation": "",
                "flash": "",
                "focal_length": "",
                "aperture": "",
                "shutter_speed": "",
                "iso": "",
                "white_balance": "",
                "metering_mode": "",
                "exposure_mode": "",
                "scene_type": "",
                "lens_model": "",
                "software": "",
                
                # Geolocation
                "latitude": "",
                "longitude": "",
                "altitude": "",
                "gps_timestamp": "",
                "gps_direction": "",
                "gps_speed": "",
                "location_name": ""
            }
            
            # Add file dates if from file path
            if isinstance(image_source, str):
                file_stats = os.stat(image_source)
                info["created_date"] = datetime.fromtimestamp(file_stats.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
                info["modified_date"] = datetime.fromtimestamp(file_stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            else:
                info["created_date"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                info["modified_date"] = info["created_date"]
            
            # Extract EXIF data
            exif_data = img._getexif()
            if exif_data:
                # Process standard EXIF tags
                for tag_id, value in exif_data.items():
                    tag = TAGS.get(tag_id, tag_id)
                    
                    if tag == "Make":
                        info["camera_make"] = str(value).strip()
                    elif tag == "Model":
                        info["camera_model"] = str(value).strip()
                    elif tag == "DateTime":
                        info["datetime_taken"] = str(value)
                    elif tag == "Orientation":
                        orientations = {
                            1: "Normal",
                            2: "Mirrored horizontal",
                            3: "Rotated 180°",
                            4: "Mirrored vertical",
                            5: "Mirrored horizontal, rotated 90° CCW",
                            6: "Rotated 90° CW",
                            7: "Mirrored horizontal, rotated 90° CW",
                            8: "Rotated 90° CCW"
                        }
                        info["orientation"] = orientations.get(value, f"Unknown ({value})")
                    elif tag == "Flash":
                        info["flash"] = "Yes" if value & 1 else "No"
                    elif tag == "FocalLength":
                        if isinstance(value, tuple) and len(value) == 2:
                            info["focal_length"] = f"{value[0]/value[1]:.1f}mm"
                        else:
                            info["focal_length"] = f"{value}mm"
                    elif tag == "FNumber":
                        if isinstance(value, tuple) and len(value) == 2:
                            info["aperture"] = f"f/{value[0]/value[1]:.1f}"
                        else:
                            info["aperture"] = f"f/{value}"
                    elif tag == "ExposureTime":
                        if isinstance(value, tuple) and len(value) == 2:
                            if value[0] == 1:
                                info["shutter_speed"] = f"1/{value[1]}s"
                            else:
                                info["shutter_speed"] = f"{value[0]/value[1]:.2f}s"
                        else:
                            info["shutter_speed"] = f"{value}s"
                    elif tag == "ISOSpeedRatings":
                        info["iso"] = str(value)
                    elif tag == "WhiteBalance":
                        wb_modes = {0: "Auto", 1: "Manual"}
                        info["white_balance"] = wb_modes.get(value, f"Unknown ({value})")
                    elif tag == "MeteringMode":
                        metering_modes = {
                            0: "Unknown", 1: "Average", 2: "Center-weighted average",
                            3: "Spot", 4: "Multi-spot", 5: "Pattern", 6: "Partial"
                        }
                        info["metering_mode"] = metering_modes.get(value, f"Unknown ({value})")
                    elif tag == "ExposureMode":
                        exposure_modes = {0: "Auto", 1: "Manual", 2: "Auto bracket"}
                        info["exposure_mode"] = exposure_modes.get(value, f"Unknown ({value})")
                    elif tag == "SceneType":
                        info["scene_type"] = "Directly photographed" if value == 1 else f"Unknown ({value})"
                    elif tag == "LensModel":
                        info["lens_model"] = str(value).strip()
                    elif tag == "Software":
                        info["software"] = str(value).strip()
                    elif tag == "GPSInfo":
                        # Process GPS information
                        gps_info = _extract_gps_info(value)
                        info.update(gps_info)
            
            # Remove empty fields for cleaner result
            info = {k: v for k, v in info.items() if v != ""}
            
            return info
            
    except Exception as e:
        return {"error": f"Error processing image: {str(e)}"}

def _extract_gps_info(gps_data):
    """
    Extract GPS information from EXIF data.
    
    Args:
        gps_data (dict): GPS data from EXIF
        
    Returns:
        dict: Geolocation information
    """
    gps_info = {
        "latitude": "",
        "longitude": "",
        "altitude": "",
        "gps_timestamp": "",
        "gps_direction": "",
        "gps_speed": "",
        "location_name": ""
    }
    
    if not gps_data:
        return gps_info
    
    try:
        # Convert GPS data to readable format
        gps_dict = {}
        for tag_id, value in gps_data.items():
            tag = GPSTAGS.get(tag_id, tag_id)
            gps_dict[tag] = value
        
        # Extract latitude
        if 'GPSLatitude' in gps_dict and 'GPSLatitudeRef' in gps_dict:
            lat = gps_dict['GPSLatitude']
            lat_ref = gps_dict['GPSLatitudeRef']
            latitude = _convert_to_degrees(lat)
            if lat_ref == 'S':
                latitude = -latitude
            gps_info["latitude"] = f"{latitude:.6f}"
        
        # Extract longitude
        if 'GPSLongitude' in gps_dict and 'GPSLongitudeRef' in gps_dict:
            lon = gps_dict['GPSLongitude']
            lon_ref = gps_dict['GPSLongitudeRef']
            longitude = _convert_to_degrees(lon)
            if lon_ref == 'W':
                longitude = -longitude
            gps_info["longitude"] = f"{longitude:.6f}"
        
        # Extract altitude
        if 'GPSAltitude' in gps_dict:
            alt = gps_dict['GPSAltitude']
            if isinstance(alt, tuple) and len(alt) == 2:
                altitude = alt[0] / alt[1]
                alt_ref = gps_dict.get('GPSAltitudeRef', 0)
                if alt_ref == 1:
                    altitude = -altitude
                gps_info["altitude"] = f"{altitude:.2f}m"
        
        # Extract GPS timestamp
        if 'GPSTimeStamp' in gps_dict and 'GPSDateStamp' in gps_dict:
            time_stamp = gps_dict['GPSTimeStamp']
            date_stamp = gps_dict['GPSDateStamp']
            if len(time_stamp) == 3:
                hours = int(time_stamp[0])
                minutes = int(time_stamp[1])
                seconds = int(time_stamp[2])
                gps_info["gps_timestamp"] = f"{date_stamp} {hours:02d}:{minutes:02d}:{seconds:02d} UTC"
        
        # Extract direction
        if 'GPSImgDirection' in gps_dict:
            direction = gps_dict['GPSImgDirection']
            if isinstance(direction, tuple) and len(direction) == 2:
                direction_degrees = direction[0] / direction[1]
                gps_info["gps_direction"] = f"{direction_degrees:.1f}°"
        
        # Extract speed
        if 'GPSSpeed' in gps_dict:
            speed = gps_dict['GPSSpeed']
            if isinstance(speed, tuple) and len(speed) == 2:
                speed_val = speed[0] / speed[1]
                speed_ref = gps_dict.get('GPSSpeedRef', 'K')
                unit = {'K': 'km/h', 'M': 'mph', 'N': 'knots'}.get(speed_ref, 'km/h')
                gps_info["gps_speed"] = f"{speed_val:.1f} {unit}"
        
        # Extract location name (if available)
        if 'GPSAreaInformation' in gps_dict:
            gps_info["location_name"] = str(gps_dict['GPSAreaInformation'])
        
    except Exception as e:
        # If there's an error processing GPS, return empty dict
        pass
    
    return gps_info

def _convert_to_degrees(value):
    """
    Convert GPS coordinates to decimal degrees.
    
    Args:
        value (tuple): Tuple with degrees, minutes, seconds
        
    Returns:
        float: Coordinate in decimal degrees
    """
    if len(value) != 3:
        return 0.0
    
    degrees = value[0]
    minutes = value[1] 
    seconds = value[2]
    
    # Convert fractions to decimal
    if isinstance(degrees, tuple):
        degrees = degrees[0] / degrees[1]
    if isinstance(minutes, tuple):
        minutes = minutes[0] / minutes[1]
    if isinstance(seconds, tuple):
        seconds = seconds[0] / seconds[1]
    
    return degrees + (minutes / 60.0) + (seconds / 3600.0)

def resize_image(image_source: Union[str, bytes], width: int, height: int,
                 maintain_aspect_ratio: bool = True, quality: int = 85) -> bytes:
    """
    Resize an image to specified dimensions and return as bytes.
    
    Args:
        image_source: Path to image file (str) or image bytes (bytes)
        width: Target width in pixels
        height: Target height in pixels
        maintain_aspect_ratio: Whether to maintain aspect ratio (default: True)
        quality: JPEG quality for output (1-100, default: 85)
        
    Returns:
        bytes: Resized image as byte array
        
    Raises:
        ValueError: If dimensions are invalid or image cannot be processed
    """
    logger.info(f"Resizing image to {width}x{height} (maintain_ratio: {maintain_aspect_ratio})")
    
    try:
        # Validate dimensions
        if width <= 0 or height <= 0:
            raise ValueError("Width and height must be positive integers")
        
        if quality < 1 or quality > 100:
            raise ValueError("Quality must be between 1 and 100")
        
        # Load image using utility function
        img, filename, file_size = _load_image_from_source(image_source)
        
        with img:
            original_width, original_height = img.size
            logger.debug(f"Original dimensions: {original_width}x{original_height}")
            
            if maintain_aspect_ratio:
                # Calculate aspect ratios
                aspect_ratio = original_width / original_height
                target_ratio = width / height
                
                if target_ratio > aspect_ratio:
                    # Target is wider, adjust width based on height
                    new_height = height
                    new_width = int(height * aspect_ratio)
                else:
                    # Target is taller, adjust height based on width
                    new_width = width
                    new_height = int(width / aspect_ratio)
            else:
                new_width, new_height = width, height
            
            logger.debug(f"New dimensions: {new_width}x{new_height}")
            
            # Resize image using high-quality resampling
            resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Convert to RGB if necessary for JPEG
            if resized_img.mode in ('RGBA', 'LA', 'P'):
                # Create white background for transparency
                background = Image.new('RGB', resized_img.size, (255, 255, 255))
                if resized_img.mode == 'P':
                    resized_img = resized_img.convert('RGBA')
                background.paste(resized_img, mask=resized_img.split()[-1] if resized_img.mode in ('RGBA', 'LA') else None)
                resized_img = background
            
            # Save to bytes
            output_buffer = io.BytesIO()
            resized_img.save(output_buffer, format='JPEG', quality=quality, optimize=True)
            image_bytes = output_buffer.getvalue()
            
            logger.info(f"Image resized successfully. New size: {len(image_bytes)} bytes")
            return image_bytes
            
    except Exception as e:
        logger.error(f"Error resizing image: {str(e)}")
        raise ValueError(f"Error resizing image: {str(e)}")

def enhance_image_for_ocr(image_source: Union[str, bytes], contrast_factor: float = 2.0, threshold: int = 128) -> bytes:
    """
    Enhance image for better OCR accuracy using multiple preprocessing techniques.
    
    Args:
        image_source: Path to image file (str) or image bytes (bytes)
        contrast_factor: Contrast enhancement factor (default: 2.0)
        threshold: Threshold value for binarization (0-255, default: 128)
        
    Returns:
        bytes: Enhanced image as byte array
        
    Raises:
        ValueError: If image cannot be processed or parameters are invalid
    """
    logger.info("Enhancing image for OCR processing")
    
    try:
        # Validate parameters
        if threshold < 0 or threshold > 255:
            raise ValueError("Threshold must be between 0 and 255")
        
        if contrast_factor <= 0:
            raise ValueError("Contrast factor must be positive")
        
        # Load image using utility function
        img, filename, file_size = _load_image_from_source(image_source)
        
        with img:
            logger.debug(f"Original image: {img.size[0]}x{img.size[1]}, mode: {img.mode}")
            
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Step 1: Convert to grayscale
            grayscale = img.convert('L')
            logger.debug("Converted to grayscale")
            
            # Step 2: Enhance contrast
            enhancer = ImageEnhance.Contrast(grayscale)
            enhanced = enhancer.enhance(contrast_factor)
            logger.debug(f"Enhanced contrast with factor {contrast_factor}")
            
            # Step 3: Sharpen the image
            sharpened = enhanced.filter(ImageFilter.SHARPEN)
            logger.debug("Applied sharpening")
            
            # Step 4: Apply median filter to reduce noise
            denoised = sharpened.filter(ImageFilter.MedianFilter(size=3))
            logger.debug("Applied noise reduction")
            
            # Step 5: Apply threshold/binarization
            enhanced = denoised.point(lambda x: 0 if x < threshold else 255, mode='1')
            logger.debug(f"Applied binarization with threshold {threshold}")

            # Save to bytes
            output_buffer = io.BytesIO()
            enhanced.save(output_buffer, format='PNG', optimize=True)
            image_bytes = output_buffer.getvalue()
            
            logger.info(f"Image enhanced successfully for OCR. New size: {len(image_bytes)} bytes")
            return image_bytes
            
    except Exception as e:
        logger.error(f"Error enhancing image for OCR: {str(e)}")
        raise ValueError(f"Error enhancing image for OCR: {str(e)}")

import pytest
import os
import io
import tempfile
from PIL import Image
from fbpyutils.image import resize_image, enhance_image_for_ocr, _load_image_from_source


class TestImageResize:
    """Test cases for image resizing functionality."""
    
    def create_test_image(self, width=100, height=100, mode='RGB'):
        """Helper to create a test image."""
        img = Image.new(mode, (width, height), color='red')
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        return buffer.getvalue()
    
    def test_resize_image_from_bytes(self):
        """Test resizing image from bytes."""
        original_bytes = self.create_test_image(200, 200)
        resized_bytes = resize_image(original_bytes, 100, 100)
        
        assert isinstance(resized_bytes, bytes)
        assert len(resized_bytes) > 0
        
        # Verify the image was actually resized
        resized_img = Image.open(io.BytesIO(resized_bytes))
        assert resized_img.size == (100, 100)
    
    def test_resize_image_from_file(self):
        """Test resizing image from file path."""
        original_bytes = self.create_test_image(200, 200)
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            tmp_file.write(original_bytes)
            tmp_path = tmp_file.name
        
        try:
            resized_bytes = resize_image(tmp_path, 100, 100)
            assert isinstance(resized_bytes, bytes)
            
            resized_img = Image.open(io.BytesIO(resized_bytes))
            assert resized_img.size == (100, 100)
        finally:
            os.unlink(tmp_path)
    
    def test_resize_image_maintain_aspect_ratio(self):
        """Test resizing with aspect ratio maintained."""
        original_bytes = self.create_test_image(400, 200)  # 2:1 aspect ratio
        resized_bytes = resize_image(original_bytes, 100, 100, maintain_aspect_ratio=True)
        
        resized_img = Image.open(io.BytesIO(resized_bytes))
        width, height = resized_img.size
        
        # Should maintain 2:1 ratio
        assert width == 100
        assert height == 50  # 100 / 2 = 50
    
    def test_resize_image_ignore_aspect_ratio(self):
        """Test resizing ignoring aspect ratio."""
        original_bytes = self.create_test_image(400, 200)
        resized_bytes = resize_image(original_bytes, 100, 100, maintain_aspect_ratio=False)
        
        resized_img = Image.open(io.BytesIO(resized_bytes))
        assert resized_img.size == (100, 100)
    
    def test_resize_image_invalid_dimensions(self):
        """Test error handling for invalid dimensions."""
        original_bytes = self.create_test_image(100, 100)
        
        with pytest.raises(ValueError, match="Width and height must be positive integers"):
            resize_image(original_bytes, -100, 100)
        
        with pytest.raises(ValueError, match="Width and height must be positive integers"):
            resize_image(original_bytes, 100, 0)
    
    def test_resize_image_invalid_quality(self):
        """Test error handling for invalid quality values."""
        original_bytes = self.create_test_image(100, 100)
        
        with pytest.raises(ValueError, match="Quality must be between 1 and 100"):
            resize_image(original_bytes, 50, 50, quality=0)
        
        with pytest.raises(ValueError, match="Quality must be between 1 and 100"):
            resize_image(original_bytes, 50, 50, quality=101)


class TestImageEnhancement:
    """Test cases for image enhancement functionality."""
    
    def create_test_image(self, width=100, height=100, mode='RGB'):
        """Helper to create a test image."""
        img = Image.new(mode, (width, height), color='red')
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        return buffer.getvalue()
    
    def test_enhance_image_basic(self):
        """Test basic image enhancement."""
        original_bytes = self.create_test_image(100, 100)
        enhanced_bytes = enhance_image_for_ocr(original_bytes)

        assert isinstance(enhanced_bytes, bytes)
        assert len(enhanced_bytes) > 0

        # Verify it's a valid image
        enhanced_img = Image.open(io.BytesIO(enhanced_bytes))
        assert enhanced_img.mode == '1'  # Should be binary
    
    def test_enhance_image_with_contrast(self):
        """Test enhancement with custom contrast."""
        original_bytes = self.create_test_image(100, 100)
        enhanced_bytes = enhance_image_for_ocr(original_bytes, contrast_factor=2.0)

        assert isinstance(enhanced_bytes, bytes)
        enhanced_img = Image.open(io.BytesIO(enhanced_bytes))
        assert enhanced_img.mode == '1'
    
    def test_enhance_image_with_threshold(self):
        """Test enhancement with threshold binarization."""
        original_bytes = self.create_test_image(100, 100)
        enhanced_bytes = enhance_image_for_ocr(original_bytes, threshold=128)
        
        assert isinstance(enhanced_bytes, bytes)
        enhanced_img = Image.open(io.BytesIO(enhanced_bytes))
        assert enhanced_img.mode == '1'  # Should be binary
    
    def test_enhance_image_invalid_threshold(self):
        """Test error handling for invalid threshold."""
        original_bytes = self.create_test_image(100, 100)
        
        with pytest.raises(ValueError, match="Threshold must be between 0 and 255"):
            enhance_image_for_ocr(original_bytes, threshold=-1)
        
        with pytest.raises(ValueError, match="Threshold must be between 0 and 255"):
            enhance_image_for_ocr(original_bytes, threshold=256)
    
    def test_enhance_image_from_file(self):
        """Test enhancement from file path."""
        original_bytes = self.create_test_image(100, 100)

        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            tmp_file.write(original_bytes)
            tmp_path = tmp_file.name

        try:
            enhanced_bytes = enhance_image_for_ocr(tmp_path)
            assert isinstance(enhanced_bytes, bytes)

            enhanced_img = Image.open(io.BytesIO(enhanced_bytes))
            assert enhanced_img.mode == '1'
        finally:
            os.unlink(tmp_path)


class TestLoadImageFromSource:
    """Test cases for the _load_image_from_source utility function."""
    
    def create_test_image(self, width=100, height=100, mode='RGB'):
        """Helper to create a test image."""
        img = Image.new(mode, (width, height), color='red')
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        return buffer.getvalue()
    
    def test_load_image_from_bytes(self):
        """Test loading image from bytes."""
        image_bytes = self.create_test_image(100, 100)
        img, filename, file_size = _load_image_from_source(image_bytes)
        
        assert img is not None
        assert filename == "image_from_bytes"
        assert file_size == len(image_bytes)
        assert img.size == (100, 100)
    
    def test_load_image_from_file(self):
        """Test loading image from file path."""
        image_bytes = self.create_test_image(100, 100)
        
        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                tmp_file.write(image_bytes)
                tmp_path = tmp_file.name
            
            img, filename, file_size = _load_image_from_source(tmp_path)
            
            assert img is not None
            assert filename.endswith('.png')
            assert file_size == os.path.getsize(tmp_path)
            assert img.size == (100, 100)
        finally:
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.unlink(tmp_path)
                except (OSError, PermissionError):
                    # Handle Windows permission issues gracefully
                    pass
    
    def test_load_image_invalid_bytes(self):
        """Test error handling for invalid bytes."""
        with pytest.raises(ValueError, match="Error loading image"):
            _load_image_from_source(b"invalid image data")
    
    def test_load_image_nonexistent_file(self):
        """Test error handling for nonexistent file."""
        with pytest.raises(ValueError, match="File not found"):
            _load_image_from_source("/nonexistent/file.png")
    
    def test_load_image_empty_bytes(self):
        """Test error handling for empty bytes."""
        with pytest.raises(ValueError, match="Empty byte array provided"):
            _load_image_from_source(b"")
    
    def test_load_image_invalid_type(self):
        """Test error handling for invalid input type."""
        with pytest.raises(ValueError, match="Invalid input type"):
            _load_image_from_source(123)

#!/usr/bin/env python3
"""
Tests for computer_mcp_client module
"""
import sys
import os

# Add parent directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../lib"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import unittest
from computer_mcp_client import WeiboAutomation


class TestBboxToCenter(unittest.TestCase):
    """Tests for bbox_to_center function"""
    
    def setUp(self):
        self.weibo = WeiboAutomation()
    
    def test_valid_bbox(self):
        """Test valid bbox conversion"""
        bbox = [0.47, 0.25, 0.61, 0.30]
        result = self.weibo.bbox_to_center(bbox)
        self.assertAlmostEqual(result[0], 0.54, places=3)
        self.assertAlmostEqual(result[1], 0.275, places=3)
    
    def test_unit_bbox(self):
        """Test unit bbox [0, 0, 1, 1]"""
        bbox = [0.0, 0.0, 1.0, 1.0]
        result = self.weibo.bbox_to_center(bbox)
        self.assertAlmostEqual(result[0], 0.5, places=3)
        self.assertAlmostEqual(result[1], 0.5, places=3)
    
    def test_small_bbox(self):
        """Test small bbox values"""
        bbox = [0.1, 0.2, 0.3, 0.4]
        result = self.weibo.bbox_to_center(bbox)
        self.assertAlmostEqual(result[0], 0.2, places=3)
        self.assertAlmostEqual(result[1], 0.3, places=3)
    
    def test_invalid_length(self):
        """Test bbox with wrong length"""
        with self.assertRaises(ValueError) as context:
            self.weibo.bbox_to_center([0.1, 0.2, 0.3])  # Only 3 elements
        self.assertIn("4 elements", str(context.exception))
        
        with self.assertRaises(ValueError) as context:
            self.weibo.bbox_to_center([0.1, 0.2, 0.3, 0.4, 0.5])  # 5 elements
        self.assertIn("4 elements", str(context.exception))
    
    def test_invalid_type(self):
        """Test bbox with non-numeric values"""
        with self.assertRaises(ValueError) as context:
            self.weibo.bbox_to_center(["a", 0.2, 0.3, 0.4])
        self.assertIn("number", str(context.exception))
        
        with self.assertRaises(ValueError) as context:
            self.weibo.bbox_to_center([0.1, None, 0.3, 0.4])
        self.assertIn("number", str(context.exception))
    
    def test_out_of_range(self):
        """Test bbox values out of [0, 1] range"""
        with self.assertRaises(ValueError) as context:
            self.weibo.bbox_to_center([1.5, 0.2, 0.3, 0.4])
        self.assertIn("0.0 and 1.0", str(context.exception))
        
        with self.assertRaises(ValueError) as context:
            self.weibo.bbox_to_center([-0.1, 0.2, 0.3, 0.4])
        self.assertIn("0.0 and 1.0", str(context.exception))
    
    def test_wrong_order_x(self):
        """Test X1 >= X2"""
        with self.assertRaises(ValueError) as context:
            self.weibo.bbox_to_center([0.6, 0.2, 0.3, 0.4])  # X1 > X2
        self.assertIn("X1", str(context.exception))
        
        with self.assertRaises(ValueError) as context:
            self.weibo.bbox_to_center([0.3, 0.2, 0.3, 0.4])  # X1 == X2
        self.assertIn("X1", str(context.exception))
    
    def test_wrong_order_y(self):
        """Test Y1 >= Y2"""
        with self.assertRaises(ValueError) as context:
            self.weibo.bbox_to_center([0.1, 0.5, 0.3, 0.4])  # Y1 > Y2
        self.assertIn("Y1", str(context.exception))
        
        with self.assertRaises(ValueError) as context:
            self.weibo.bbox_to_center([0.1, 0.4, 0.3, 0.4])  # Y1 == Y2
        self.assertIn("Y1", str(context.exception))


class TestBboxToScreenCoords(unittest.TestCase):
    """Tests for bbox_to_screen_coords function"""
    
    def setUp(self):
        self.weibo = WeiboAutomation()
    
    def test_conversion(self):
        """Test bbox to screen coordinates conversion"""
        bbox = [0.47, 0.25, 0.61, 0.30]
        window_rect = {"left": 100, "top": 50, "width": 1200, "height": 800}
        result = self.weibo.bbox_to_screen_coords(bbox, window_rect)
        # center_x = (0.47 + 0.61) / 2 = 0.54
        # center_y = (0.25 + 0.30) / 2 = 0.275
        # screen_x = 100 + int(1200 * 0.54) = 100 + 648 = 748
        # screen_y = 50 + int(800 * 0.275) = 50 + 220 = 270
        self.assertEqual(result[0], 748)
        self.assertEqual(result[1], 270)
    
    def test_zero_origin(self):
        """Test with zero origin window"""
        bbox = [0.5, 0.5, 0.7, 0.7]
        window_rect = {"left": 0, "top": 0, "width": 1000, "height": 800}
        result = self.weibo.bbox_to_screen_coords(bbox, window_rect)
        # center_x = (0.5 + 0.7) / 2 = 0.6
        # center_y = (0.5 + 0.7) / 2 = 0.6
        # screen_x = 0 + int(1000 * 0.6) = 600
        # screen_y = 0 + int(800 * 0.6) = 480
        self.assertEqual(result[0], 600)
        self.assertEqual(result[1], 480)
    
    def test_missing_window_rect_keys(self):
        """Test window_rect missing required keys"""
        bbox = [0.1, 0.2, 0.3, 0.4]
        
        with self.assertRaises(ValueError) as context:
            self.weibo.bbox_to_screen_coords(bbox, {"left": 0, "top": 0, "width": 100})  # missing height
        self.assertIn("height", str(context.exception))
        
        with self.assertRaises(ValueError) as context:
            self.weibo.bbox_to_screen_coords(bbox, {"top": 0, "width": 100, "height": 100})  # missing left
        self.assertIn("left", str(context.exception))
    
    def test_invalid_window_rect_types(self):
        """Test window_rect with invalid types"""
        bbox = [0.1, 0.2, 0.3, 0.4]
        
        with self.assertRaises(ValueError) as context:
            self.weibo.bbox_to_screen_coords(bbox, {"left": "0", "top": 0, "width": 100, "height": 100})
        self.assertIn("integer", str(context.exception))


if __name__ == "__main__":
    unittest.main()

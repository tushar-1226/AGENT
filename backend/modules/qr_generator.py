"""
QR Code Generator Module
Generate QR codes with various customization options
"""
from typing import Optional
import io
import base64

try:
    import qrcode
    from qrcode.image.styledpil import StyledPilImage
    from qrcode.image.styles.moduledrawers import RoundedModuleDrawer, CircleModuleDrawer, GappedSquareModuleDrawer
    from qrcode.image.styles.colormasks import SolidFillColorMask
    QRCODE_AVAILABLE = True
except ImportError:
    QRCODE_AVAILABLE = False
    print("QRCode library not available. Install with: pip install qrcode[pil]")


class QRCodeGenerator:
    """Generate QR codes with various styles and formats"""
    
    def __init__(self):
        if not QRCODE_AVAILABLE:
            raise ImportError("qrcode library is required. Install with: pip install qrcode[pil]")
    
    def generate_qr_code(
        self,
        data: str,
        size: int = 10,
        border: int = 4,
        fill_color: str = "black",
        back_color: str = "white",
        error_correction: str = "M",
        style: str = "square"
    ) -> dict:
        """
        Generate QR code and return as base64 encoded image
        
        Args:
            data: The data to encode in the QR code
            size: Size of the QR code (box_size parameter)
            border: Border size in boxes
            fill_color: Color of the QR code modules
            back_color: Background color
            error_correction: Error correction level (L, M, Q, H)
            style: Module style (square, rounded, circle, gapped)
        
        Returns:
            dict with base64 encoded image and metadata
        """
        
        # Error correction levels
        error_correction_map = {
            'L': qrcode.constants.ERROR_CORRECT_L,
            'M': qrcode.constants.ERROR_CORRECT_M,
            'Q': qrcode.constants.ERROR_CORRECT_Q,
            'H': qrcode.constants.ERROR_CORRECT_H
        }
        
        # Create QR code instance
        qr = qrcode.QRCode(
            version=1,  # Auto-adjust
            error_correction=error_correction_map.get(error_correction, qrcode.constants.ERROR_CORRECT_M),
            box_size=size,
            border=border,
        )
        
        # Add data
        qr.add_data(data)
        qr.make(fit=True)
        
        # Convert colors to RGB tuples for styled images
        from PIL import ImageColor
        try:
            front_rgb = ImageColor.getrgb(fill_color)
            back_rgb = ImageColor.getrgb(back_color)
        except:
            front_rgb = fill_color
            back_rgb = back_color
        
        # Create image with style
        if style == "rounded":
            module_drawer = RoundedModuleDrawer()
        elif style == "circle":
            module_drawer = CircleModuleDrawer()
        elif style == "gapped":
            module_drawer = GappedSquareModuleDrawer()
        else:
            module_drawer = None
        
        if module_drawer:
            img = qr.make_image(
                image_factory=StyledPilImage,
                module_drawer=module_drawer,
                color_mask=SolidFillColorMask(back_color=back_rgb, front_color=front_rgb)
            )
        else:
            img = qr.make_image(fill_color=fill_color, back_color=back_color)
        
        # Convert to base64
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return {
            "success": True,
            "image_base64": f"data:image/png;base64,{img_str}",
            "format": "PNG",
            "size": f"{img.size[0]}x{img.size[1]}",
            "data_length": len(data),
            "error_correction": error_correction,
            "style": style
        }
    
    def generate_qr_svg(self, data: str, size: int = 10, border: int = 4) -> dict:
        """
        Generate QR code as SVG
        
        Args:
            data: The data to encode
            size: Size multiplier
            border: Border size
            
        Returns:
            dict with SVG string
        """
        try:
            import qrcode.image.svg
            
            factory = qrcode.image.svg.SvgPathImage
            
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=size,
                border=border,
                image_factory=factory
            )
            
            qr.add_data(data)
            qr.make(fit=True)
            
            img = qr.make_image()
            
            # Save to string buffer
            buffered = io.BytesIO()
            img.save(buffered)
            svg_str = buffered.getvalue().decode('utf-8')
            
            return {
                "success": True,
                "svg": svg_str,
                "format": "SVG",
                "data_length": len(data)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def generate_wifi_qr(self, ssid: str, password: str, security: str = "WPA") -> dict:
        """
        Generate WiFi QR code
        
        Args:
            ssid: WiFi network name
            password: WiFi password
            security: Security type (WPA, WEP, nopass)
            
        Returns:
            dict with QR code data
        """
        wifi_string = f"WIFI:T:{security};S:{ssid};P:{password};;"
        return self.generate_qr_code(wifi_string)
    
    def generate_vcard_qr(self, name: str, phone: str = "", email: str = "", 
                         organization: str = "", url: str = "") -> dict:
        """
        Generate vCard (contact) QR code
        
        Args:
            name: Full name
            phone: Phone number
            email: Email address
            organization: Company/Organization
            url: Website URL
            
        Returns:
            dict with QR code data
        """
        vcard = f"BEGIN:VCARD\nVERSION:3.0\nFN:{name}\n"
        
        if phone:
            vcard += f"TEL:{phone}\n"
        if email:
            vcard += f"EMAIL:{email}\n"
        if organization:
            vcard += f"ORG:{organization}\n"
        if url:
            vcard += f"URL:{url}\n"
        
        vcard += "END:VCARD"
        
        return self.generate_qr_code(vcard, error_correction="H")
    
    def generate_event_qr(self, summary: str, location: str = "", 
                         start_time: str = "", end_time: str = "", 
                         description: str = "") -> dict:
        """
        Generate calendar event QR code
        
        Args:
            summary: Event title
            location: Event location
            start_time: Start datetime (ISO format)
            end_time: End datetime (ISO format)
            description: Event description
            
        Returns:
            dict with QR code data
        """
        # Convert to iCalendar format
        event = f"BEGIN:VEVENT\nSUMMARY:{summary}\n"
        
        if location:
            event += f"LOCATION:{location}\n"
        if start_time:
            event += f"DTSTART:{start_time.replace('-', '').replace(':', '')}\n"
        if end_time:
            event += f"DTEND:{end_time.replace('-', '').replace(':', '')}\n"
        if description:
            event += f"DESCRIPTION:{description}\n"
        
        event += "END:VEVENT"
        
        return self.generate_qr_code(event, error_correction="H")
    
    def batch_generate(self, data_list: list, **kwargs) -> list:
        """
        Generate multiple QR codes
        
        Args:
            data_list: List of data strings to encode
            **kwargs: Additional parameters for generate_qr_code
            
        Returns:
            list of QR code results
        """
        results = []
        
        for data in data_list:
            try:
                result = self.generate_qr_code(data, **kwargs)
                results.append(result)
            except Exception as e:
                results.append({
                    "success": False,
                    "error": str(e),
                    "data": data
                })
        
        return results

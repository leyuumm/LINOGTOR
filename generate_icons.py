"""
Generate PWA icons for LINOGTOR
"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(size, filename):
    """Create a simple icon with earthquake symbol"""
    # Create image with gradient background
    img = Image.new('RGB', (size, size), color='#3b82f6')
    draw = ImageDraw.Draw(img)
    
    # Create gradient effect (blue to darker blue)
    for y in range(size):
        intensity = int(59 + (118 - 59) * (y / size))
        blue = int(246 - (246 - 200) * (y / size))
        for x in range(size):
            draw.point((x, y), fill=(intensity, intensity, blue))
    
    # Draw earthquake symbol (simplified seismograph wave)
    wave_color = '#ffffff'
    center_y = size // 2
    amplitude = size // 6
    
    # Draw wave pattern
    points = []
    for x in range(0, size, 2):
        if x < size // 4:
            y = center_y
        elif x < size // 2:
            y = center_y - amplitude + (x - size//4) * amplitude * 2 // (size//4)
        elif x < 3*size // 4:
            y = center_y + amplitude - (x - size//2) * amplitude * 2 // (size//4)
        else:
            y = center_y
        points.append((x, y))
    
    # Draw the wave
    if len(points) > 1:
        draw.line(points, fill=wave_color, width=max(size//20, 3))
    
    # Draw circle at center (epicenter)
    circle_radius = size // 8
    draw.ellipse(
        [size//2 - circle_radius, center_y - circle_radius,
         size//2 + circle_radius, center_y + circle_radius],
        fill=wave_color,
        outline=wave_color
    )
    
    # Add ripple effect
    for i in range(1, 4):
        ripple_radius = circle_radius + (i * size // 20)
        draw.ellipse(
            [size//2 - ripple_radius, center_y - ripple_radius,
             size//2 + ripple_radius, center_y + ripple_radius],
            outline=wave_color,
            width=max(size//40, 1)
        )
    
    # Save the icon
    img.save(filename, 'PNG')
    print(f"✅ Created {filename} ({size}x{size})")

def main():
    """Generate all required icon sizes"""
    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    os.makedirs(static_dir, exist_ok=True)
    
    # Generate icons for different sizes
    sizes = {
        'icon-16.png': 16,
        'icon-32.png': 32,
        'icon-152.png': 152,
        'icon-167.png': 167,
        'icon-180.png': 180,
        'icon-192.png': 192,
        'icon-512.png': 512,
        'icon-apple-touch.png': 180
    }
    
    print("🎨 Generating PWA icons for LINOGTOR...")
    for filename, size in sizes.items():
        filepath = os.path.join(static_dir, filename)
        create_icon(size, filepath)
    
    print("\n✨ All icons generated successfully!")
    print("📱 LINOGTOR is now ready as a Progressive Web App!")

if __name__ == '__main__':
    main()

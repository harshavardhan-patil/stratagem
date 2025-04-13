import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Arc
from pycirclize import Circos
import os  # Import the os module

def create_circular_chart(filename="img1.jpg"):
    """
    Creates and saves a circular sector chart.
    """
    np.random.seed(0)

    # Define 6 sectors and corresponding colors
    sectors = {"Market Deep": 10, "Partnerships": 10, "Optimization": 10, "East Africa": 10, "Data Driven": 10, "Sustainability": 10}  # Changed sector names
    sector_colors = {
        "Market Deep": "#00A89D",  # Teal
        "Partnerships": "#0078AC",  # Cyan-blue
        "Optimization": "#4C67A1",  # Soft blue
        "East Africa": "#6C55A3",  # Purple
        "Data Driven": "#955AA1",  # Violet
        "Sustainability": "#A85F98",  # Magenta-lavender
    }

    # Initialize Circos plot
    circos = Circos(sectors, space=2)

    # Plot each sector with a unique color
    for sector in circos.sectors:
        sector.text(f"{sector.name}", r=106, size=12, color="black")

        x = np.arange(sector.start, sector.end) + 0.5
        y = np.random.randint(50, 100, len(x))  # Just some dummy data

        # Track with filled color like a donut slice
        donut_track = sector.add_track((75, 100), r_pad_ratio=0.05)
        donut_track.axis(fc=sector_colors[sector.name])

    # Plot the figure
    fig = circos.plotfig()
    plt.savefig(filename)
    plt.close(fig)  # Close the figure to free memory


def create_roadmap_chart(filename="img2.jpg"):
    """
    Creates and saves the marketing roadmap chart.
    """
    # Set up the figure
    fig, ax = plt.subplots(figsize=(14, 8), facecolor='white')
    ax.set_aspect('equal')
    ax.axis('off')

    # Define colors for each quarter
    colors = {
        'Q1': '#00A89D',  # Teal
        'Q2': '#0078AC',  # Cyan-blue
        'Q3': '#6C55A3',  # Purple
        'Q4': '#A85F98'  # Magenta-lavender
    }

    # Create quarter arcs that form a continuous flow
    # Q1 - Top left - Teal
    q1_arc = Arc((-2, 0), 4, 4, theta1=90, theta2=180,
                 linewidth=40, color=colors['Q1'], alpha=0.9)
    ax.add_patch(q1_arc)

    # Q2 - Bottom left - Cyan-blue
    q2_arc = Arc((-2, 0), 4, 4, theta1=0, theta2=90,
                 linewidth=40, color=colors['Q2'], alpha=0.9)
    ax.add_patch(q2_arc)

    # Q3 - Bottom right - Purple
    q3_arc = Arc((2, 0), 4, 4, theta1=-90, theta2=0,
                 linewidth=40, color=colors['Q3'], alpha=0.9)
    ax.add_patch(q3_arc)

    # Q4 - Top right - Magenta-lavender
    q4_arc = Arc((2, 0), 4, 4, theta1=-180, theta2=-90,
                 linewidth=40, color=colors['Q4'], alpha=0.9)
    ax.add_patch(q4_arc)

    # Add title and company info
    plt.text(-3, 4, "GreenHarvest - 3 Month Plan", fontsize=22, fontweight='bold')
    plt.text(-3, 3.5, "Laying the groundwork for longer-term growth.", fontsize=11)

    # Set axis limits
    plt.xlim(-7, 7)
    plt.ylim(-4.5, 4.5)

    # Q1 Content
    plt.text(-6.5, 2.8, "Market Deep", fontsize=11, color='#00A89D', fontweight='bold')
    plt.text(-6.5, 2.0, "Steps:", fontsize=11, color='#00A89D', fontweight='bold')
    plt.text(-6.5, 1.6, "• Research target countries", color='#00A89D', fontsize=10)
    plt.text(-6.5, 1.2, "• Gather farmer feedback", color='#00A89D', fontsize=10)
    plt.text(-6.5, 0.8, "• Analyze data deployments", color='#00A89D', fontsize=10)

    # Q2 Content
    plt.text(-6.5, -1.0, "Partnerships", fontsize=11, color='#0078AC', fontweight='bold')
    plt.text(-6.5, -2.2, "Steps:", fontsize=11, color='#0078AC', fontweight='bold')
    plt.text(-6.5, -2.6, "• Engage potential partners", color='#0078AC', fontsize=10)
    plt.text(-6.5, -3.2, "• Develop proposals", color='#0078AC', fontsize=10)

    # Q3 Content - shifted to the right side
    plt.text(4, -1.0, "Optimization", fontsize=11, color='#6C55A3', fontweight='bold')
    plt.text(4, -2.2, "Steps:", fontsize=11, color='#6C55A3', fontweight='bold')
    plt.text(4, -2.6, "• Refine product features", color='#6C55A3', fontsize=10)
    plt.text(4, -3.2, "• Develop pricing model", color='#6C55A3', fontsize=10)

    # Q4 Content
    plt.text(1.4, 2.8, "Go-To-Market", fontsize=11, color='#A85F98', fontweight='bold')
    plt.text(1, 1.2, "Steps:", fontsize=11, color='#A85F98', fontweight='bold')
    plt.text(1, 0.8, "• Launch pilot program", color='#A85F98', fontsize=10)
    plt.text(1, 0.5, "• Prepare marketing", color='#A85F98', fontsize=10)

    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close(fig) # Close the figure to free memory

# Generate the plots and save them as images in the root directory
create_circular_chart(filename="img1.jpg")
create_roadmap_chart(filename="img2.jpg")

print("Images saved as img1.jpg and img2.jpg in the root directory.")

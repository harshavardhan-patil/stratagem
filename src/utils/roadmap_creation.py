from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

def generate_roadmap(chat_history):
    API_KEY = os.getenv("GOOGLE_API_KEY")
    client = genai.Client(api_key=API_KEY)

    # Prompt examples
    prompt = chat_history

    # Original base code
    python_code_topics = '''from pycirclize import Circos
    import numpy as np

    np.random.seed(0)

    # Define 6 sectors and corresponding colors
    sectors = {"A": 10, "B": 10, "C": 10, "D": 10, "E": 10, "F": 10}
    sector_colors = {
        "A": "#00A89D",  # Teal
        "B": "#0078AC",  # Cyan-blue
        "C": "#4C67A1",  # Soft blue
        "D": "#6C55A3",  # Purple
        "E": "#955AA1",  # Violet
        "F": "#A85F98",  # Magenta-lavender
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
    fig.savefig("circular_sector_chart.png")
    '''

    python_code_roadmap = '''import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib.patches import Arc

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
    # ax.text(-2.1, 2.1, "Q1", fontsize=36, fontweight='bold', color=colors['Q1'], ha='center', va='center')

    # Q2 - Bottom left - Cyan-blue
    q2_arc = Arc((-2, 0), 4, 4, theta1=0, theta2=90, 
            linewidth=40, color=colors['Q2'], alpha=0.9)
    ax.add_patch(q2_arc)
    # ax.text(-2.1, -2.1, "Q2", fontsize=36, fontweight='bold', color=colors['Q2'], ha='center', va='center')

    # Q3 - Bottom right - Purple
    q3_arc = Arc((2, 0), 4, 4, theta1=-90, theta2=0, 
            linewidth=40, color=colors['Q3'], alpha=0.9)
    ax.add_patch(q3_arc)
    # ax.text(2.1, -2.1, "Q3", fontsize=36, fontweight='bold', color=colors['Q3'], ha='center', va='center')

    # Q4 - Top right - Magenta-lavender
    q4_arc = Arc((2, 0), 4, 4, theta1=-180, theta2=-90, 
            linewidth=40, color=colors['Q4'], alpha=0.9)
    ax.add_patch(q4_arc)
    # ax.text(2.1, 2.1, "Q4", fontsize=36, fontweight='bold', color=colors['Q4'], ha='center', va='center')

    # Add title and company info
    plt.text(-3, 4, "Marketing Strategy Roadmap 2023", fontsize=22, fontweight='bold')
    plt.text(-3, 3.5, "Go-To-Market is an advertising approach that is based on several factors such as value strategy,\nexternal marketing metrics, unique selling propositions, and distribution channels.", fontsize=11)

    # Set axis limits
    plt.xlim(-7, 7)
    plt.ylim(-4.5, 4.5)

    # Q1 Content
    plt.text(-6.5, 2.8, "Goal 1", fontsize=11, color='#00A89D', fontweight='bold')
    plt.text(-6.5, 2.0, "Steps:", fontsize=11, color='#00A89D', fontweight='bold')
    plt.text(-6.5, 1.6, "• Find your target audience.", color='#00A89D', fontsize=10)
    plt.text(-6.5, 1.2, "• Work on market segmentation.", color='#00A89D', fontsize=10)
    plt.text(-6.5, 0.8, "• Determine your lead generation strategies.", color='#00A89D', fontsize=10)
    plt.text(-6.5, 0.4, "• Craft a proper pricing strategy", color='#00A89D', fontsize=10)

    # Q2 Content
    plt.text(-6.5, -1.0, "Goal 2", fontsize=11, color='#0078AC', fontweight='bold')
    plt.text(-6.5, -2.2, "Steps:", fontsize=11, color='#0078AC', fontweight='bold')
    plt.text(-6.5, -2.6, "• Assess the top features and benefits of your", color='#0078AC', fontsize=10)
    plt.text(-6.5, -2.9, "  product.", fontsize=10)
    plt.text(-6.5, -3.2, "• Find out the solutions that can solve your", color='#0078AC', fontsize=10)
    plt.text(-6.5, -3.5, "  user's problems.", color='#0078AC', fontsize=10)
    plt.text(-6.5, -3.8, "• Allot a market-friendly price to your product.", color='#0078AC', fontsize=10)

    # Q3 Content - shifted to the right side
    plt.text(4, -1.0, "Goal:", fontsize=11, color='#6C55A3', fontweight='bold')
    plt.text(4, -2.2, "Steps:", fontsize=11, color='#6C55A3', fontweight='bold')
    plt.text(4, -2.6, "• Find out how you are going to introduce your", color='#6C55A3', fontsize=10)
    plt.text(4, -2.9, "  product to the target market.", color='#6C55A3', fontsize=10)
    plt.text(4, -3.2, "• Try to differentiate your products from that", color='#6C55A3', fontsize=10)
    plt.text(4, -3.5, "  of the competitors.", color='#6C55A3', fontsize=10)
    plt.text(4, -3.8, "• Keep adjusting your product strategy, as per", color='#6C55A3', fontsize=10)
    plt.text(4, -4.1, "  the customer needs.", color='#6C55A3', fontsize=10)


    # Q4 Content
    plt.text(1.4, 2.8, "Goal:", fontsize=11, color='#A85F98', fontweight='bold')
    plt.text(1, 1.2, "Steps:", fontsize=11, color='#A85F98', fontweight='bold')
    plt.text(1, 0.8, "• Determine the objectives of your strategy.", color='#A85F98', fontsize=10)
    plt.text(1, 0.5, "• Be clear on your target audience and boost", color='#A85F98', fontsize=10)
    plt.text(1, 0.2, "  your chances of success.", color='#A85F98', fontsize=10)

    plt.tight_layout()
    plt.savefig('marketing_roadmap_final.png', dpi=150, bbox_inches='tight')
    plt.show()
    '''
    # Combine prompt + code
    full_prompt = f"""Please modify the Python code below to reflect the insights from the given strategic prompt example and generate circular visualization using python code.
    Make sure it is two to three words in each sector and not more than that and it replaces A, B, C in sectors dictionary and sector colors dictionary.

    Python Code:
    {python_code_topics}

    Prompt:
    {prompt}

    Please modify the Python code below to reflect the insights from the given strategic prompt example and generate visualization using python code.
    Make sure goal is replaced by the topic highlighted and it is two to five words only and other text can be changed based on the topic on how to take the action.

    Python Code:
    {python_code_roadmap}

    Prompt :
    {prompt}


    Now create a python code named as combined_viz.py which incorporates both python codes generated above and ensures that plots generate are saved in the format img1.jpg, img2.jpg and so on.

    Please do generate the 6 month and 1 year plan if details are mentioned in the prompt similar to that of 3 month plan. Again combine all the slides using the presentation code provided earlier.

    Python Code:
    {python_code_roadmap}

    Prompt :
    {prompt}

    """

    # Send to Gemini
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=full_prompt
    )



    # Try to extract the new Python code from the response
    import re

    if hasattr(response, "text"):
        code_blocks = re.findall(r"```(?:python)?\n(.*?)```", response.text, re.DOTALL)
        updated_code = code_blocks[0] if code_blocks else response.text.strip()
    else:
        updated_code = response.strip()

    # Save updated code to new.py
    with open("combined_viz.py", "w") as f:
        f.write(updated_code)

    print("✅ combined_viz.py has been updated with Gemini's modified code.")
  
    os.system("python3 combined_viz.py")
    return True
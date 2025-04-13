from google import genai

client = genai.Client(api_key="AIzaSyAvVxeWVhKEx0Q-3UOdjfyC2cZXHT_czEw")

# Prompt examples
prompt_examples = """
Example:
3-Month Plan: Foundation & Validation
Objective: Solidify product-market fit and prepare for scaling.
Key Activities:
Refine Go-to-Market Strategy (GTM):
Conduct in-depth market research in target regions (East Africa and Southeast Asia) to understand specific farmer needs, infrastructure limitations, and competitive landscape. (Reference: "Sustainable Growth Strategy for Agritech Startup in Precision Farming," https://flevy.com/topic/total-shareholder-value/case-sustainable-growth-strategy-agritech-startup-precision-farming).
Identify and prioritize "Star" markets with high growth potential and alignment with GreenHarvest's capabilities, using the Growth-Share Matrix framework.
Develop localized marketing materials and training programs, considering language, cultural nuances, and access to technology. * Optimize Tiered Pricing Model:
Analyze price sensitivity among target farmers and develop a tiered pricing model that balances affordability with profitability.
Explore financing options and partnerships with rural banks and microfinance institutions to make solutions accessible to farmers with limited capital.
Enhance AI-Powered Crop Predictions:
Refine AI algorithms for crop monitoring and pest/disease detection using data collected from existing deployments.
Develop predictive models for supply chain optimization to minimize post-harvest losses and improve market access for farmers.
Investor Persona Development:
Identify potential investor personas (e.g., impact investors, venture capitalists, agricultural funds) and tailor pitch decks to their specific interests and investment criteria.
Focus on showcasing GreenHarvest's social impact, scalability, and potential for financial returns.
Key Performance Indicators (KPIs):
Number of farmers engaged in market research activities.
Completion rate of localized marketing materials and training programs.
Accuracy of AI-powered crop predictions.
Number of investor meetings secured.
II. 6-Month Plan: Expansion & Partnerships* Objective: Expand market reach and establish strategic partnerships.
Key Activities:
Market Expansion through Strategic Partnerships:
Forge partnerships with NGOs, agricultural departments, and rural banks to leverage their existing networks and expertise. (Reference: "Sustainable Growth Strategy for Agritech Startup in Precision Farming," https://flevy.com/topic/total-shareholder-value/case-sustainable-growth-strategy-agritech-startup-precision-farming).
Develop joint marketing campaigns and training programs with partners to promote adoption of GreenHarvest's solutions.
Pilot Programs in New Regions:
Launch pilot programs in selected regions of East Africa and Southeast Asia, focusing on demonstrating the value of GreenHarvest's solutions to local farmers.
Collect data on crop yields, farmer satisfaction, and adoption rates to refine the GTM strategy and product offerings.
Secure Seed Funding:
Actively pitch to identified investor personas, highlighting the results of pilot programs and the potential for scaling.
Develop a detailed financial model and business plan to demonstrate the long-term sustainability of GreenHarvest's business model.
Supply Chain Optimization:
Implement strategies to reduce logistics costs for hardware delivery and maintenance, such as establishing local distribution centers and training local technicians.
Key Performance Indicators (KPIs):
Number of strategic partnerships established.
Number of farmers participating in pilot programs.
Crop yield improvements in pilot regions.
Amount of seed funding secured.
Reduction in logistics costs.
III. 1-Year Plan: Scaling & Innovation
Objective: Scale operations, drive innovation, and establish GreenHarvest as a leader in affordable smart farming solutions.
Key Activities:
Scale Operations in Target Regions:
Expand sales and marketing efforts in successful pilot regions, leveraging partnerships and local networks.
Establish a robust customer support system to ensure farmer satisfaction and retention.
Product Development & Innovation:
Invest in R&D to develop next-generation precision farming technologies, focusing on AI-powered solutions for supply chain optimization and crop prediction. (Reference: "Sustainable Growth Strategy for Agritech Startup in Precision Farming," https://flevy.com/topic/total-shareholder-value/case-sustainable-growth-strategy-agritech-startup-precision-farming).
Explore the use of blockchain technology to improve transparency and traceability in agricultural supply chains.
Impact Measurement & Reporting:
Develop a system for tracking and reporting on the social and environmental impact of GreenHarvest's solutions, such as improvements in farmer livelihoods, reductions in water usage, and decreases in pesticide application.
Use impact data to attract impact investors and demonstrate the value of GreenHarvest's solutions to stakeholders.
Team Expansion:
Recruit talent with expertise in sales, marketing, technology, and operations to support scaling efforts.
Foster a culture of innovation and collaboration to drive continuous improvement and product development.
Key Performance Indicators (KPIs):
Number of farmers reached.
Revenue growth.
Customer satisfaction score.
Social and environmental impact metrics (e.g., farmer income, water usage, pesticide reduction).
Employee engagement score.
Key Strategic Considerations:
Technology Adoption: Address farmer resistance to new technology through education, training, and demonstrating clear benefits. (Reference: "Revenue Growth Strategy for Agritech Startup," https://flevy.com/topic/company-analysis/case-revenue-growth-strategy-agritech-startup).
Infrastructure Limitations: Develop solutions that are compatible with limited internet access and infrastructure in rural areas.
Financial Sustainability: Balance affordability with profitability to ensure the long-term sustainability of the business model.
Competitive Landscape: Continuously monitor the competitive landscape and differentiate GreenHarvest's solutions through superior technology, localized offerings, and strong customer support.
Data Privacy and Security: Implement robust data privacy and security measures to protect farmer data and maintain trust.
This one-year plan provides a framework for GreenHarvest Technologies to achieve sustainable growth and make a positive impact on the lives of smallholder farmers. Remember to regularly review and adjust the plan based on market conditions, customer feedback, and performance data.

"""

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

Prompt Example:
{prompt_examples}

Please modify the Python code below to reflect the insights from the given strategic prompt example and generate visualization using python code.
Make sure goal is replaced by the topic highlighted and it is two to five words only and other text can be changed based on the topic on how to take the action.

Python Code:
{python_code_roadmap}

Prompt Example:
{prompt_examples}


Now create a python code named as combined_viz.py which incorporates both python codes generated above and ensures that two images are added in the slide on different pages using the provided code.

prs = Presentation()
slide_layout = prs.slide_layouts[1]  # blank layout
slide = prs.slides.add_slide(slide_layout)
left = Inches(1)
top = Inches(1)
height = Inches(5.5)
slide.shapes.add_picture(image_path, left, top, height=height)

slide_layout = prs.slide_layouts[1]  # blank layout
slide = prs.slides.add_slide(slide_layout)
left = Inches(1)
top = Inches(1)
height = Inches(5.5)
slide.shapes.add_picture(image_path, left, top, height=height)

# Save the presentation
pptx_path = os.path.join(os.getcwd(), "combined_chart.pptx")
prs.save(pptx_path)
print(f'✅ PowerPoint saved to')

Please do generate the 6 month and 1 year plan if details are mentioned in the prompt similar to that of 3 month plan. Again combine all the slides using the presentation code provided earlier.

Python Code:
{python_code_roadmap}

Prompt Example:
{prompt_examples}

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
"""
Phase 2 Fixtures Generator: Produces 12 realistic educational PDF documents across all subjects.
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import fitz # PyMuPDF
from PIL import Image, ImageDraw, ImageFont

FIXTURES_DIR = r"C:\Users\jvris\Downloads\pod-siksha\tests\fixtures\phase2_documents"
os.makedirs(FIXTURES_DIR, exist_ok=True)

styles = getSampleStyleSheet()
title_style = styles['Title']
h1_style = styles['Heading1']
h2_style = styles['Heading2']
normal_style = styles['Normal']

code_style = ParagraphStyle(
    'CodeStyle',
    parent=styles['Normal'],
    fontName='Courier',
    fontSize=9,
    leading=12,
    textColor=colors.HexColor('#1A2320')
)

def build_pdf(filename, flowables):
    path = os.path.join(FIXTURES_DIR, filename)
    doc = SimpleDocTemplate(path, pagesize=letter, leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=40)
    doc.build(flowables)
    print(f"Generated: {filename} ({os.path.getsize(path)} bytes)")
    return path

# 1. Python Programming PDF
def gen_python():
    flow = [
        Paragraph("Advanced Python: Iterators, Generators and Recursion", title_style),
        Spacer(1, 10),
        Paragraph("1. Recursive Algorithms and Call Stacks", h1_style),
        Paragraph("Recursion is a technique where a function calls itself to solve smaller subproblems until a base condition is reached.", normal_style),
        Spacer(1, 8),
        Preformatted("""def recursive_fibonacci(n: int) -> int:
    \"\"\"Calculates the n-th Fibonacci number with recursive branching.\"\"\"
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    # Recursive reduction
    return recursive_fibonacci(n - 1) + recursive_fibonacci(n - 2)

# Sample Execution
if __name__ == '__main__':
    values = [recursive_fibonacci(i) for i in range(8)]
    print(f'Fibonacci Sequence: {values}')""", code_style),
        Spacer(1, 10),
        Paragraph("2. Algorithmic Complexity Analysis", h2_style),
        Paragraph("The naive recursive Fibonacci algorithm exhibits exponential time complexity O(2^n). Using memoization or dynamic programming reduces execution to linear time O(n).", normal_style)
    ]
    return build_pdf("01_python_programming.pdf", flow)

# 2. Java OOP PDF
def gen_java():
    flow = [
        Paragraph("Object-Oriented Programming with Java: Polymorphism & Interfaces", title_style),
        Spacer(1, 10),
        Paragraph("1. Abstract Base Classes and Inheritance Hierarchies", h1_style),
        Paragraph("In Java, abstraction allows decoupling contract definitions from concrete execution logic using interfaces and abstract classes.", normal_style),
        Spacer(1, 8),
        Preformatted("""package edu.podsiksha.shapes;

public abstract class GeometricShape {
    protected String color;

    public GeometricShape(String color) {
        this.color = color;
    }

    public abstract double calculateArea();
    public abstract double calculatePerimeter();
}

public class Circle extends GeometricShape {
    private double radius;

    public Circle(String color, double radius) {
        super(color);
        this.radius = radius;
    }

    @Override
    public double calculateArea() {
        return Math.PI * radius * radius;
    }

    @Override
    public double calculatePerimeter() {
        return 2 * Math.PI * radius;
    }
}""", code_style)
    ]
    return build_pdf("02_java_oop.pdf", flow)

# 3. DSA PDF
def gen_dsa():
    flow = [
        Paragraph("Data Structures & Algorithms: Binary Search Trees (BST)", title_style),
        Spacer(1, 10),
        Paragraph("1. Tree Properties and Search Invariants", h1_style),
        Paragraph("A Binary Search Tree enforces the strict invariant that for every node X, all values in its left subtree are strictly smaller than X, and all values in its right subtree are strictly greater.", normal_style),
        Spacer(1, 8),
        Preformatted("""class BSTNode:
    def __init__(self, key: int):
        self.key = key
        self.left = None
        self.right = None

def bst_insert(root: BSTNode, key: int) -> BSTNode:
    if root is None:
        return BSTNode(key)
    if key < root.key:
        root.left = bst_insert(root.left, key)
    elif key > root.key:
        root.right = bst_insert(root.right, key)
    return root

def bst_search(root: BSTNode, target: int) -> bool:
    if root is None:
        return False
    if root.key == target:
        return True
    elif target < root.key:
        return bst_search(root.left, target)
    return bst_search(root.right, target)""", code_style),
        Spacer(1, 10),
        Paragraph("Time Complexity: Average search time is O(log n) in balanced trees and degrades to O(n) in pathological degenerate cases.", normal_style)
    ]
    return build_pdf("03_dsa_binary_trees.pdf", flow)

# 4. Mathematics PDF
def gen_math():
    flow = [
        Paragraph("Multivariable Calculus: Integrals and Gradient Fields", title_style),
        Spacer(1, 10),
        Paragraph("1. Fundamental Theorem of Line Integrals", h1_style),
        Paragraph("Consider a scalar potential function f and a smooth curve C parameterized by r(t). The line integral through gradient field satisfies:", normal_style),
        Spacer(1, 8),
        Paragraph("$$\\int_C \\nabla f \\cdot d\\mathbf{r} = f(\\mathbf{r}(b)) - f(\\mathbf{r}(a))$$", h2_style),
        Paragraph("Where nabla f denotes the spatial gradient vector: $$\\nabla f = \\left( \\frac{\\partial f}{\\partial x}, \\frac{\\partial f}{\\partial y}, \\frac{\\partial f}{\\partial z} \\right)$$", normal_style),
        Spacer(1, 8),
        Paragraph("2. Matrix Determinant and Eigenvalue Formulation", h2_style),
        Paragraph("For an n x n transformation matrix A, characteristic polynomial solves:", normal_style),
        Paragraph("$$\\det(A - \\lambda I) = 0$$", h2_style)
    ]
    return build_pdf("04_mathematics_calculus.pdf", flow)

# 5. Biology PDF
def gen_biology():
    flow = [
        Paragraph("Cellular Energetics: Photosystem II and ATP Synthesis", title_style),
        Spacer(1, 10),
        Paragraph("1. Light-Dependent Reactions in the Thylakoid Membrane", h1_style),
        Paragraph("Photosynthesis converts solar photons into chemical potential energy stored in ATP and NADPH. Within chloroplast grana, chlorophyll pigments absorb light at wavelengths 680 nm (Photosystem II) and 700 nm (Photosystem I).", normal_style),
        Spacer(1, 8),
        Paragraph("Figure 4.1: Water Photolysis and Electron Transport Chain", h2_style),
        Paragraph("Enzymatic splitting of water molecules releases electrons and protons into the thylakoid lumen:", normal_style),
        Paragraph("$$2H_2O \\rightarrow 4H^+ + 4e^- + O_2$$", h2_style),
        Paragraph("The resulting proton electrochemical gradient drives ATP Synthase rotor kinetics, generating ATP from ADP and inorganic phosphate.", normal_style)
    ]
    return build_pdf("05_biology_cell_energetics.pdf", flow)

# 6. Chemistry PDF
def gen_chem():
    flow = [
        Paragraph("Chemical Thermodynamics: Gibbs Free Energy & Reaction Kinetics", title_style),
        Spacer(1, 10),
        Paragraph("1. Spontaneity and Chemical Equilibrium", h1_style),
        Paragraph("The thermodynamic criterion for reaction spontaneity at constant temperature and pressure is dictated by the Gibbs Free Energy change:", normal_style),
        Paragraph("$$\\Delta G = \\Delta H - T\\Delta S$$", h2_style),
        Paragraph("When Delta G < 0, the reaction proceeds exergonically (spontaneously). At dynamic equilibrium, Delta G = 0 and connects to equilibrium constant K:", normal_style),
        Paragraph("$$\\Delta G^\\circ = -RT \\ln(K_{eq})$$", h2_style)
    ]
    return build_pdf("06_chemistry_thermodynamics.pdf", flow)

# 7. Physics PDF
def gen_physics():
    flow = [
        Paragraph("Electromagnetism: Lorentz Force and Maxwell Equations", title_style),
        Spacer(1, 10),
        Paragraph("1. Charged Particles in Combined Electric and Magnetic Fields", h1_style),
        Paragraph("A particle with charge q moving with velocity v through an electric field E and magnetic flux density B experiences Lorentz Force:", normal_style),
        Paragraph("$$\\mathbf{F} = q(\\mathbf{E} + \\mathbf{v} \\times \\mathbf{B})$$", h2_style),
        Paragraph("2. Differential Formulation of Maxwell's Equations", h1_style),
        Paragraph("Gauss's Law for Magnetism: $$\\nabla \\cdot \\mathbf{B} = 0$$", normal_style),
        Paragraph("Faraday's Law of Induction: $$\\nabla \\times \\mathbf{E} = -\\frac{\\partial \\mathbf{B}}{\\partial t}$$", normal_style)
    ]
    return build_pdf("07_physics_electromagnetism.pdf", flow)

# 8. Research Paper PDF
def gen_research():
    flow = [
        Paragraph("A Comparative Evaluation of Socratic Multi-Agent Dialogue in AI Tutoring", title_style),
        Paragraph("Rishitha J.V., Pod-Siksha Research Laboratory · DOI: 10.1016/j.aied.2026.04.012", normal_style),
        Spacer(1, 8),
        Paragraph("Abstract", h2_style),
        Paragraph("We evaluate conversational learning efficiency using two-host Socratic dialogue versus traditional didactic monologue across 1,240 secondary school participants. Empirical findings demonstrate a 34% increase in concept retention.", normal_style),
        Spacer(1, 10),
        Paragraph("Methodology and Empirical Cohorts", h1_style),
        Table([
            ["Cohort", "Modality", "Participants", "Retention Rate (14 Days)"],
            ["Group A", "Static Textbook", "410", "51.4%"],
            ["Group B", "Unimodal Monologue", "415", "62.8%"],
            ["Group C", "Socratic 2-Host Dialogue", "415", "85.4%"]
        ], style=[
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#ECE7DF')),
            ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#CCCCCC')),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('PADDING', (0,0), (-1,-1), 6)
        ]),
        Spacer(1, 10),
        Paragraph("Results & Discussion", h2_style),
        Paragraph("Statistical significance confirmed via two-tailed t-test (t = 8.42, p < 0.001).", normal_style)
    ]
    return build_pdf("08_research_paper.pdf", flow)

# 9. History PDF
def gen_history():
    flow = [
        Paragraph("World History: The Industrial Revolution & Social Transformation", title_style),
        Spacer(1, 10),
        Paragraph("1. Mechanization of the Textile Industry (1760-1840)", h1_style),
        Paragraph("The transition from agrarian handicraft economies to machine-driven manufacturing began in Britain with the steam engine invented by James Watt and the spinning jenny by James Hargreaves.", normal_style),
        Spacer(1, 8),
        Paragraph("2. Socio-Economic Repercussions & Urbanization", h2_style),
        Paragraph("Rapid factory concentration catalyzed massive demographic migrations toward urban industrial centers such as Manchester and Birmingham, creating the modern industrial working class and spurring labor legislation.", normal_style)
    ]
    return build_pdf("09_history_world_war.pdf", flow)

# 10. Geography PDF
def gen_geography():
    flow = [
        Paragraph("Physical Geography: Tropical Monsoons & Atmospheric Circulation", title_style),
        Spacer(1, 10),
        Paragraph("1. Differential Thermal Heating of Landmass and Ocean", h1_style),
        Paragraph("Monsoons represent large-scale seasonal reversals in atmospheric surface winds caused by the differential specific heat capacity between the Asian landmass and the Indian Ocean.", normal_style),
        Spacer(1, 8),
        Paragraph("2. The Intertropical Convergence Zone (ITCZ) & Coriolis Deflection", h2_style),
        Paragraph("During northern hemisphere summer, intense heating of the Tibetan Plateau generates a profound low-pressure thermal trough, drawing moist maritime air northwards across the equator, deflected rightwards by the Coriolis effect.", normal_style)
    ]
    return build_pdf("10_geography_monsoons.pdf", flow)

# 11. Scanned Document PDF (Pure rasterized bitmap page)
def gen_scanned():
    # Create an image using PIL, draw text and simulated scan noise, then save into PDF
    img = Image.new("RGB", (1200, 1600), color=(248, 246, 240))
    draw = ImageDraw.Draw(img)
    # Draw simulated scanned text
    draw.text((100, 120), "ARCHIVAL MANUSCRIPT · HISTORICAL ASTRONOMY (SCANNED)", fill=(40, 40, 40))
    draw.line((100, 150, 1100, 150), fill=(100, 100, 100), width=2)
    draw.text((100, 200), "Johannes Kepler: Laws of Planetary Motion (1609)", fill=(20, 20, 20))
    draw.text((100, 260), "1. The orbit of every planet is an ellipse with the Sun at one of the two foci.", fill=(50, 50, 50))
    draw.text((100, 320), "2. A line segment joining a planet and the Sun sweeps out equal areas during equal intervals of time.", fill=(50, 50, 50))
    draw.text((100, 380), "3. The square of the orbital period of a planet is directly proportional to the cube of the semi-major axis.", fill=(50, 50, 50))
    draw.text((100, 460), "Mathematical Formulation: T^2 = k * a^3", fill=(30, 30, 30))
    
    # Add subtle scanned vignette noise lines
    for i in range(10):
        draw.line((80 + i*100, 600, 120 + i*100, 602), fill=(180, 175, 160), width=1)

    temp_img_path = os.path.join(FIXTURES_DIR, "temp_scan.png")
    img.save(temp_img_path)

    # Wrap in PDF using PyMuPDF (fitz) with zero extractable text layer
    pdf_path = os.path.join(FIXTURES_DIR, "11_scanned_manuscript.pdf")
    doc = fitz.open()
    page = doc.new_page(width=612, height=792)
    page.insert_image(page.rect, filename=temp_img_path)
    doc.save(pdf_path)
    doc.close()
    if os.path.exists(temp_img_path):
        os.remove(temp_img_path)

    print(f"Generated: 11_scanned_manuscript.pdf ({os.path.getsize(pdf_path)} bytes)")
    return pdf_path

# 12. Mixed Science and Code PDF
def gen_mixed():
    flow = [
        Paragraph("Computational Physics: Numerical Simulation of Planetary Orbits", title_style),
        Spacer(1, 10),
        Paragraph("1. Gravitational Dynamics and Differential Equations", h1_style),
        Paragraph("Newtonian gravitational acceleration vector between mass M and test particle satisfies:", normal_style),
        Paragraph("$$\\mathbf{a} = -\\frac{GM}{r^3} \\mathbf{r}$$", h2_style),
        Spacer(1, 8),
        Paragraph("2. Verlet Integration Algorithm in Python", h1_style),
        Preformatted("""import numpy as np

def verlet_step(pos: np.ndarray, vel: np.ndarray, dt: float, G: float = 6.674e-11, M: float = 1.989e30):
    \"\"\"Symplectic numerical integrator preserving orbital energy.\"\"\"
    r = np.linalg.norm(pos)
    acc = - (G * M / (r**3)) * pos
    new_pos = pos + vel * dt + 0.5 * acc * (dt**2)
    new_r = np.linalg.norm(new_pos)
    new_acc = - (G * M / (new_r**3)) * new_pos
    new_vel = vel + 0.5 * (acc + new_acc) * dt
    return new_pos, new_vel""", code_style),
        Spacer(1, 10),
        Paragraph("Table 1.1: Error Convergence of Numerical Orbit Integrators", h2_style),
        Table([
            ["Integrator", "Order", "Energy Drift (100 Orbits)", "Symplectic"],
            ["Euler-Forward", "O(dt)", "+14.82%", "No"],
            ["Runge-Kutta 4", "O(dt^4)", "+0.004%", "No"],
            ["Verlet-Velocity", "O(dt^2)", "< 0.0001%", "Yes"]
        ], style=[
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#ECE7DF')),
            ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#CCCCCC')),
            ('PADDING', (0,0), (-1,-1), 5)
        ])
    ]
    return build_pdf("12_mixed_science_and_code.pdf", flow)

if __name__ == '__main__':
    print("Generating 12 realistic educational PDF fixtures...")
    gen_python()
    gen_java()
    gen_dsa()
    gen_math()
    gen_biology()
    gen_chem()
    gen_physics()
    gen_research()
    gen_history()
    gen_geography()
    gen_scanned()
    gen_mixed()
    print("All 12 fixtures generated successfully!")

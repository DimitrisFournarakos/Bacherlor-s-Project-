#----------- ~  Comparative Performance Evaluation of Asymmetric Cryptographic Algorithms   ~ -----------
import os
import secrets
import random
import hashlib
import hmac
import string
import time
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
import matplotlib.pyplot as plt
import numpy as np

# --- METRICS COLLECTOR & EXPORT TO EXCEL ---
class MetricsCollector:
    """Συλλέγει μετρικές για κάθε αλγόριθμο"""
    def __init__(self):
        self.data = []
    
    def add_metric(self, algorithm, input_size, key_gen_speed, latency_signing, 
                   latency_verification, throughput, key_size=None, signature_size=None):
        """Προσθέτει μια εγγραφή μετρικών"""
        self.data.append({
            'Algorithm': algorithm,
            'Input_Size': input_size,
            'Throughput': throughput,
            'Key_Gen_Speed': key_gen_speed,
            'Latency_Signing': latency_signing,
            'Latency_Verification': latency_verification,           
            'Key_Size': key_size,
            'Signature_Size': signature_size,
        })
    
    def export_to_excel(self, filename='crypto_metrics.xlsx'):
        """Εξάγει τα δεδομένα σε Excel με ένα μόνο φύλλο"""
        wb = Workbook()
        ws = wb.active
        ws.title = "Αποτελέσματα"
        
        # Κεφαλίδες
        headers = ['Algorithm', 'Input_Size', 'Throughput (MB/s)','Key_Gen_Speed (ms)' ,
              'Latency_Verification (ms)', 'Latency_Signing (ms)', 'Key_Size (bytes)',
              'Signature_Size (bytes)']
        ws.append(headers)
        
        # Styling κεφαλίδας
        header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
        header_font = Font(bold=True, color="FFFFFF", size=11)
        border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )
        
        for cell in ws[1]:
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            cell.border = border
        
        # Δεδομένα
        for metric in self.data:
            row = [
                metric['Algorithm'],
                metric['Input_Size'],
                f"{metric['Throughput']:.3f}" if metric['Throughput'] is not None else "-",
                f"{metric['Key_Gen_Speed']:.3f}" if metric['Key_Gen_Speed'] is not None else "-",
                f"{metric['Latency_Verification']:.3f}" if metric['Latency_Verification'] is not None else "-",
                f"{metric['Latency_Signing']:.3f}" if metric['Latency_Signing'] is not None else "-",
                metric['Key_Size'] if metric['Key_Size'] is not None else "-",
                metric['Signature_Size'] if metric['Signature_Size'] is not None else "-",
            ]
            ws.append(row)
        
        # Styling δεδομένων
        for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
            for cell in row:
                cell.border = border
                cell.alignment = Alignment(horizontal="center", vertical="center")
        
        # Προσαρμογή πλάτους στηλών
        widths = [18, 15, 15, 18, 22, 18, 18, 22]
        for idx, width in enumerate(widths, 1):
            ws.column_dimensions[chr(64 + idx)].width = width
        
        ws.row_dimensions[1].height = 25
        
        wb.save(filename)
        print(f"✓ Αποτελέσματα αποθηκευμένα στο: {filename}")


def create_plots(metrics_collector, outdir='plots'):
    """Δημιουργεί και αποθηκεύει τα διαγράμματα με matplotlib:
    - Grouped bar chart: Latency (signing) per algorithm for each input size
    - Line chart: Throughput scalability per algorithm across input sizes
    - Stacked bar chart: Signing vs Verification latency per algorithm (aggregated)
    - Bar Chart (Signature Size & Key Size): Comparison of average signature and key sizes per algorithm
    """
    os.makedirs(outdir, exist_ok=True)

    # Συλλογή μοναδικών αλγορίθμων και μεγεθών (σε σταθερή σειρά)
    algos = []
    sizes = []
    for rec in metrics_collector.data:
        a = rec['Algorithm']
        s = rec['Input_Size']
        if a not in algos:
            algos.append(a)
        if s not in sizes:
            sizes.append(s)

    # Στάνταρ σειρά μεγεθών
    preferred_order = [f'{1000:,}', f'{10000:,}', f'{100000:,}', f'{1000000:,}']
    sizes_sorted = [s for s in preferred_order if s in sizes] + [s for s in sizes if s not in preferred_order]

    # Χτίζουμε lookup: algo -> size -> metrics
    lookup = {a: {} for a in algos}
    for rec in metrics_collector.data:
        lookup[rec['Algorithm']][rec['Input_Size']] = rec

    # Grouped bar chart (Signing latency per algorithm per input size)
    x = np.arange(len(algos))
    width = 0.8 / max(1, len(sizes_sorted))
    fig, ax = plt.subplots(figsize=(10, 6))
    for i, size in enumerate(sizes_sorted):
        latencies = [lookup[a].get(size, {}).get('Latency_Signing', np.nan) for a in algos]
        ax.bar(x + (i - (len(sizes_sorted)-1)/2) * width, latencies, width, label=size)
    ax.set_ylabel('Latency Signing (ms)')
    ax.set_title('Latency (Signing) per Algorithm and Input Size')
    ax.set_xticks(x)
    ax.set_xticklabels(algos, rotation=25)
    ax.legend(title='Input Size')
    fig.tight_layout()
    fp = os.path.join(outdir, 'latency_grouped_signing.png')
    fig.savefig(fp)
    plt.close(fig)

    # Line chart: Throughput scalability
    fig, ax = plt.subplots(figsize=(10, 6))

    # x values numeric (bytes)
    x_vals = [int(s.replace(',', '')) for s in sizes_sorted]
    x_kb = [v/1024 for v in x_vals]

    for a in algos:
        thr = [lookup[a].get(s, {}).get('Throughput', np.nan) for s in sizes_sorted]
        ax.plot(x_kb, thr, marker='o', label=a)

    ax.set_xscale('log')
    ax.set_xlabel('Input Size (KB, log scale)')
    ax.set_ylabel('Throughput (MB/s)')
    ax.set_title('Throughput Scalability per Algorithm (1KB → 1MB)')
    ax.legend()
    ax.grid(True, which='both', ls='--', lw=0.5)
    fig.tight_layout()
    fp = os.path.join(outdir, 'throughput_scalability.png')
    fig.savefig(fp)
    plt.close(fig)

    # Stacked bar chart: Signing vs Verification aggregated per algorithm (for a chosen size or averaged)
    # We'll compute the average signing and verification latency across available sizes per algorithm
    sign_avgs = []
    verify_avgs = []
    for a in algos:
        vals_sign = []
        vals_verify = []
        for s in sizes_sorted:
            rec = lookup[a].get(s)
            if rec:
                if rec.get('Latency_Signing') is not None:
                    vals_sign.append(rec.get('Latency_Signing'))
                if rec.get('Latency_Verification') is not None:
                    vals_verify.append(rec.get('Latency_Verification'))
        sign_avgs.append(np.mean(vals_sign) if vals_sign else 0)
        verify_avgs.append(np.mean(vals_verify) if vals_verify else 0)

    x = np.arange(len(algos))
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(x, sign_avgs, label='Signing (avg ms)')
    ax.bar(x, verify_avgs, bottom=sign_avgs, label='Verification (avg ms)')
    ax.set_xticks(x)
    ax.set_xticklabels(algos, rotation=25)
    ax.set_ylabel('Latency (ms)')
    ax.set_title('Signing vs Verification Latency (average across sizes)')
    ax.legend()
    fig.tight_layout()
    fp = os.path.join(outdir, 'latency_stacked_avg.png')
    fig.savefig(fp)
    plt.close(fig)

    # Signature size data used by the remaining charts
    sig_avgs = []
    sig_labels = []
    for a in algos:
        vals_sig = []
        for s in sizes_sorted:
            rec = lookup[a].get(s)
            if rec:
                v = rec.get('Signature_Size')
                if isinstance(v, (int, float)):
                    vals_sig.append(v)
        if vals_sig:
            sig_avgs.append(np.mean(vals_sig))
        else:
            # keep zero only if there was explicit 0
            sig_avgs.append(0)
        sig_labels.append(a)

    print(f"✓ Plots saved in: {outdir} (grouped, throughput, stacked)")

    # Key size vs Signature size (grouped bar chart)
    # Compute average key sizes per algorithm (aligned with sig_labels)
    key_avgs = []
    for a in sig_labels:
        vals_key = []
        for s in sizes_sorted:
            rec = lookup[a].get(s)
            if rec:
                v = rec.get('Key_Size')
                if isinstance(v, (int, float)):
                    vals_key.append(v)
        key_avgs.append(np.mean(vals_key) if vals_key else 0)

    x = np.arange(len(sig_labels))
    width = 0.35
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(x - width/2, key_avgs, width, label='Key Size (bytes)', color='tab:blue')
    ax.bar(x + width/2, sig_avgs, width, label='Signature Size (bytes)', color='tab:purple')
    ax.set_xticks(x)
    ax.set_xticklabels(sig_labels, rotation=25)
    ax.set_ylabel('Bytes')
    ax.set_title('Average Key Size vs Signature Size per Algorithm')
    ax.legend()
    
    for i, (k, s_val) in enumerate(zip(key_avgs, sig_avgs)):
        ax.text(i - width/2, k + max(1, max(key_avgs) * 0.01) if max(key_avgs) else k + 1, f"{int(k)}", ha='center', va='bottom', fontsize=8)
        ax.text(i + width/2, s_val + max(1, max(sig_avgs) * 0.01) if max(sig_avgs) else s_val + 1, f"{int(s_val)}", ha='center', va='bottom', fontsize=8)
    fig.tight_layout()
    fp = os.path.join(outdir, 'key_vs_signature_size.png')
    fig.savefig(fp)
    plt.close(fig)

    print(f"✓ Key vs Signature size chart saved in: {outdir}")

    # Bar chart for signature sizes
    x = np.arange(len(sig_labels))
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(x, sig_avgs, color='tab:purple')
    ax.set_xticks(x)
    ax.set_xticklabels(sig_labels, rotation=25)
    ax.set_ylabel('Signature Size (bytes)')
    ax.set_title('Average Signature Size per Algorithm')
    for i, v in enumerate(sig_avgs):
        ax.text(i, v + max(1, max(sig_avgs) * 0.01), f"{int(v)}", ha='center', va='bottom')
    fig.tight_layout()
    fp = os.path.join(outdir, 'signature_size_bar.png')
    fig.savefig(fp)
    plt.close(fig)

    print(f"✓ Signature size charts saved in: {outdir}")


# --- RANDOM GENERATOR ΓΙΑ DATASET ---
def generate_dataset(seed=None, sizes=None):
    """
    Δημιουργεί datasets με διαφορετικά μεγέθη χαρακτήρων.
    Χρησιμοποιεί seeded random για reproducible αποτελέσματα.
    
    Args:
        seed (int): Optional seed για reproducible αποτελέσματα
        sizes (list): Λίστα με τα μεγέθη των texts (default: [1000, 10000, 100000, 1000000])
        
    Returns:
        dict: Λεξικό με κλειδιά το μέγεθος και τιμές το text
    """
    if seed is None:
        seed = int(time.time() * 1000) % (2**32) #Χρησιμοποιεί τον τρέχοντα χρόνο σε milliseconds ως seed αν δεν δοθεί, για να έχουμε διαφορετικά δεδομένα κάθε φορά που τρέχει το πρόγραμμα.
    
    if sizes is None:
        sizes = [1000, 10000, 100000, 1000000]
    
    rng = random.Random(seed) # Δημιουργεί ένα αντικείμενο random με το συγκεκριμένο seed για να έχουμε reproducible αποτελέσματα. Αυτό σημαίνει ότι κάθε φορά που τρέχουμε τη συνάρτηση με τον ίδιο seed, θα πάρουμε τα ίδια τυχαία δεδομένα.
    charset = string.ascii_letters + string.digits + string.punctuation + " " #Ορίζει το σύνολο χαρακτήρων που θα χρησιμοποιηθούν για τη δημιουργία των τυχαίων κειμένων. Περιλαμβάνει όλα τα γράμματα (κεφαλαία και πεζά), τους αριθμούς, τα σημεία στίξης και το κενό.
    
    dataset = {}
    print(f"Δημιουργία dataset με seed={seed}...\n")
    
    for size in sizes:
        print(f"-> Δημιουργία text {size:,} χαρακτήρων...", end=" ", flush=True)
        start_time = time.time()
        text = ''.join(rng.choice(charset) for _ in range(size)) # Επιλέγει τυχαία size χαρακτήρες από το charset και τους ενώνει(join) σε ένα ενιαίο string.Η for ουσιαστικά επιλέγει τυχαίο χαρακτήρα από το charset ξανά και ξανά, συνολικά size φορές".
        elapsed = time.time() - start_time # Υπολογίζει τον χρόνο που χρειάστηκε για να δημιουργηθεί το text.
        dataset[size] = text # Αποθηκεύει το δημιουργημένο text στο λεξικό dataset με το μέγεθος ως κλειδί.
        print(f"✓ ({elapsed:.3f}s)") # Εκτυπώνει ένα μήνυμα επιβεβαίωσης με το χρόνο που χρειάστηκε για τη δημιουργία του text, μορφoπoιώντας τον χρόνο με 3 δεκαδικά ψηφία.
    
    print() # Προσθέτω μια κενή γραμμή στο τέλος της δημιουργίας του dataset για καλύτερη εμφάνιση στο terminal.
    return dataset


# --- ΒΟΗΘΗΤΙΚΕΣ ΜΑΘΗΜΑΤΙΚΕΣ ΣΥΝΑΡΤΗΣΕΙΣ ---
def gcd(a, b): # Εύρεση Μέγιστου Κοινού Διαιρέτη
    while b:
        a, b = b, a % b
    return a

def lcms(a, b): # Εύρεση Ελάχιστου Κοινού Πολλαπλάσιου
    return abs(a * b) // gcd(a, b)

def mod_inverse(a, m):
    """Υπολογισμός αντίστροφου a στο modulo m με Extended Euclidean Algorithm"""
    def extended_gcd(a, b):# Υλοποίηση του Extended Euclidean Algorithm
        
        if a == 0:
            return b, 0, 1 #gcd(0,b)=b --> (b,0,1),άρα x=0, y=1 ώστε 0⋅x+b⋅y=b, ουσιαστικα το b=gcd(a,b) και τα x,y είναι οι συντελεστές 
        
        #Εδώ γίνεται αναδρομή με τα νέα a και b, 
        #όπου το νέο a είναι το υπόλοιπο της διαίρεσης του b με το a, 
        #και το νέο b είναι το παλιό a. Αυτό συνεχίζεται μέχρι να φτάσουμε στη βάση της αναδρομής όπου a=0.
        gcd_val, x1, y1 = extended_gcd(b % a, a) #(bmoda, a)
        x = y1 - (b // a) * x1 #γυρίζει πίσω τη λύση από το μικρότερο πρόβλημα στο αρχικό.
        y = x1

        return gcd_val, x, y #gcd_val(μέγιστος κοινός διαιρέτης) και συντελεστές
    
    #Κρατάμε μόνο το x = Καλεί τον Extended Euclid για τους αριθμούς a mod m και m, και επιστρέφει το x που είναι ο αντίστροφος του a modulo m.
    _, x, _ = extended_gcd(a % m, m)
    return (x % m + m) % m#επιστρέφει τον «κανονικοποιημένο» modular inverse,για να μην έχουμε αρνητικές τιμές



# --- ΕΛΛΕΙΠΤΙΚΕΣ ΚΑΜΠΥΛΕΣ ΣΗΜΕΙΑ (Elliptic Curves) ---
class EllipticCurve:
    """Κλάση που αντιπροσωπεύει ελλειπτική καμπύλη y² ≡ x³ + ax + b (mod p)"""
    
    def __init__(self, a, b, p, order=None):
        self.a = a
        self.b = b
        self.p = p  # Πρώτος αριθμός (modulo)
        self.order = order  # Τάξη της ομάδας (αριθμός σημείων)
    
    def __eq__(self, other):
        """Έλεγχος ισότητας δύο καμπυλών"""
        return self.a == other.a and self.b == other.b and self.p == other.p
    
class Point:
    """Κλάση που αντιπροσωπεύει σημείο στην ελλειπτική καμπύλη y² ≡ x³ + ax + b (mod p) & functions για την υλοποίηση πράξεων πάνω στην καμπύλη"""
    
    def __init__(self, x, y, curve):
        self.x = x
        self.y = y
        self.curve = curve
        # Έλεγχος αν το σημείο είναι στην καμπύλη
        if x is not None and y is not None:
            left = (y * y) % curve.p #υπολογίζει το y² mod p
            right = (x**3 + curve.a * x + curve.b) % curve.p #υπολογίζει το x³ + ax + b mod p
            if left != right: #ελέγχει αν το σημείο ικανοποιεί την εξίσωση της καμπύλης,αν όχι, τότε δεν είναι σημείο της καμπύλης και βγάζει σφάλμα
                raise ValueError(f"Point ({x}, {y}) is not on the curve")
    
    def is_identity(self):
        """Έλεγχος αν είναι το σημείο στο άπειρο (point at infinity)"""
        return self.x is None and self.y is None
    
    def __add__(self, other):
        """Πρόσθεση σημείων στην ελλειπτική καμπύλη"""

        if not isinstance(other, Point):#Ελέγχει ότι το other είναι αντικείμενο τύπου Point πριν γίνει η πρόσθεση σημείων στην add.Προσθέτω μόνο σημεία με σημεία.
            raise TypeError("Can only add Point to Point")
        if self.curve != other.curve:#Ελέγχει ότι και τα δύο σημεία ανήκουν στην ίδια ελλειπτική καμπύλη (ίδια a, b, p).
            raise ValueError("Points are on different curves")
        
        # Αν ένα από τα σημεία είναι το σημείο στο άπειρο
        if self.is_identity():
            return Point(other.x, other.y, self.curve)
        if other.is_identity():
            return Point(self.x, self.y, self.curve)
        
        # Αν τα σημεία έχουν ίδιο x, τότε είτε είναι αντίθετα είτε είναι το ίδιο σημείο.
        if self.x == other.x:
            if (self.y + other.y) % self.curve.p == 0:
                return Point(None, None, self.curve)
            if self == other:
                # Διπλασιασμός σημείου: λ = (3x₁² + a) / (2y₁) mod p
                numerator = (3 * self.x**2 + self.curve.a) % self.curve.p
                denominator = (2 * self.y) % self.curve.p
            else:
                raise ValueError("Invalid point addition on the same x-coordinate")
        else:
            # Πρόσθεση δύο διαφορετικών σημείων.
            numerator = (other.y - self.y) % self.curve.p #Αριθμητής για την κλίση (slope) λ = (y₂ - y₁) / (x₂ - x₁) mod p
            denominator = (other.x - self.x) % self.curve.p #Παρανομαστής για την κλίση (slope) λ = (y₂ - y₁) / (x₂ - x₁) mod p
        
        # Υπολογισμός slope (κλίση) με αντίστροφο του παρανομαστή,Διαίρεση με τον παρονομαστή στο πεδίο modulo σημαίνει να πολλαπλασιάζουμε με τον αντίστροφό του.
        denominator_inv = mod_inverse(denominator, self.curve.p)
        slope = (numerator * denominator_inv) % self.curve.p
        
        # Υπολογισμός νέου σημείου
        x3 = (slope**2 - self.x - other.x) % self.curve.p
        y3 = (slope * (self.x - x3) - self.y) % self.curve.p
        
        return Point(x3, y3, self.curve)
    
    def __mul__(self, scalar):
        """Βαθμωτός πολλαπλασιασμός σημείου (scalar * P) - Binary method"""
        if not isinstance(scalar, int):
            raise TypeError("Can only multiply Point by an integer")
        
        scalar = scalar % self.curve.order #Μειώνει το scalar modulo την τάξη της ομάδας (order).
        result = Point(None, None, self.curve) #Αρχικοποιεί το αποτέλεσμα στο ουδέτερο στοιχείο της ομάδας, το σημείο στο άπειρο O.(π.χ. O + P = P για κάθε σημείο P στην καμπύλη)
        addend = Point(self.x, self.y, self.curve) #Βάζει σε προσωρινή μεταβλητή το αρχικό σημείο (self) P που θα διπλασιάζεται/προστίθεται στον βρόχο binary method.
        
        while scalar:
            #Κάνε bitwise AND του scalar με το 1
            #Ελέγχει αν το λιγότερο σημαντικό bit του scalar είναι 1.(0001,αρα είναι! γιατι το τελευταίο bit είναι 1)
            if scalar & 1: #αν αποτέλεσμα είναι 1 → ο scalar είναι περιττός.
                result = result + addend
            addend = addend + addend #αν αποτέλεσμα είναι 0 → ο scalar είναι άρτιος.
            scalar >>= 1 #right shift κατά 1 θέση,δηλαδή διαιρεί το scalar δια 2 και κρατάω το ακέραιο μέρος. Αυτό προετοιμάζει το scalar για τον επόμενο γύρο του βρόχου, όπου θα ελέγξουμε το επόμενο bit.
        return result
    

    def __rmul__(self, scalar): #O P * k δουλεύει κανονικά με την __mul__,όμως αν k * P,τότε πετάει TypeError,για αυτό έχω βάλει την συγκεκριμένη συνάρτηση.
        """Δεξιός πολλαπλασιασμός"""
        return self * scalar
    
    #Αυτά τα δυο functions είναι πιο πολύ για debugging και εμφάνιση του αντικειμένου, δεν επηρεάζουν τη λειτουργικότητα της πρόσθεσης και του πολλαπλασιασμού σημείων.
    def __eq__(self, other):
        """Έλεγχος ισότητας δύο σημείων"""
        return self.x == other.x and self.y == other.y
    
    def __repr__(self):#Ελέγχει αν το σημείο είναι το σημείο στο άπειρο.
        #Αυτό το function είναι για να βλέπω το αντικείμενο στο debugger/console,Το αντικείμενο εμφανίζεται μέσα σε λίστες/dicts.
        if self.is_identity():
            return "Point(∞)"
        return f"Point({self.x}, {self.y})"



# --- ED25519 HELPERS ---
# Οι παρακάτω συναρτήσεις υλοποιούν τις βασικές λειτουργίες για το Ed25519, όπως πρόσθεση σημείων, πολλαπλασιασμό με βαθμωτό, κωδικοποίηση σημείων, δημιουργία κλειδιών και επαλήθευση υπογραφών.
#Οι σταθερές του προτύπου Ed25519 (RFC 8032) που ορίζουν την καμπύλη Ed25519 και το σημείο βάσης (base point) χρησιμοποιούνται για τις λειτουργίες υπογραφής και επαλήθευσης. 
#Παράμετροι πεδίου/ομάδας: ED25519_P, ED25519_L  , Παράμετροι καμπύλης: ED25519_A, ED25519_D  , Σημείο βάσης: ED25519_BASE_POINT, Σημείο ταυτότητας: ED25519_IDENTITY
ED25519_P = 2**255 - 19 #Είναι ο “χώρος αριθμών” που δουλεύει η καμπύλη,όλα γίνονται με υπόλοιπα mod αυτόν τον αριθμό
                                                            #scalar = πόσες φορές θα κινηθούμε πάνω στην καμπύλη από ένα σημείο.
ED25519_L = 2**252 + 27742317777372353535851937790883648493 # O αριθμός(η τάξη) των σημείων που υπάρχουν στην καμπύλη. Χρησιμοποιείται για να περιορίσει τα scalars στο σωστό εύρος και να διασφαλίσει την ασφάλεια του σχήματος υπογραφής.
ED25519_D = (-121665 * pow(121666, -1, ED25519_P)) % ED25519_P #σταθερός αριθμός που ορίζει το σχήμα της καμπύλης.
ED25519_A = ED25519_P - 1 #μία σταθερά που χρησιμοποιείται στην εξίσωση της καμπύλης. Η καμπύλη Ed25519 ορίζεται από την εξίσωση: -x² + y² = 1 + dx²y² mod p, όπου a=-1 και d=ED25519_D.
ED25519_BASE_POINT = ( #Σημείο Εκκίνησης,Φτιάχνω δημόσιο κλειδί και υπογραφές με πολλαπλασιασμό,με αυτή την σταθερά
    15112221349535400772501151409588531511454012693041857206046113283949847762202,
    46316835694926478169428394003475163141307993866256225615783033603165251855960,
)
ED25519_IDENTITY = (0, 1) #Μηδενικό σημείο της ομάδας,αν το προσθέσουμε σε σημείο, δεν αλλάζει τίποτα.


def ed25519_is_identity(point):
    return point == ED25519_IDENTITY


def ed25519_point_add(point_a, point_b):
    if ed25519_is_identity(point_a):
        return point_b
    if ed25519_is_identity(point_b):
        return point_a
    
    """ Παίρνει δύο σημεία της Ed25519 και εφαρμόζει τον  τύπο πρόσθεσης για να βρει το τρίτο σημείο"""
    x1, y1 = point_a #Α = (x1,y1)
    x2, y2 = point_b #Β = (x2,y2)
    x1x2 = (x1 * x2) % ED25519_P #Υπολογίζει το x1 * x2 mod p, που είναι μέρος του τύπου πρόσθεσης για την καμπύλη Ed25519.
    y1y2 = (y1 * y2) % ED25519_P #Υπολογίζει το y1 * y2 mod p, που είναι επίσης μέρος του τύπου πρόσθεσης για την καμπύλη Ed25519.
    x1y2 = (x1 * y2) % ED25519_P #Υπολογίζει το x1 * y2 mod p, που είναι μέρος του τύπου πρόσθεσης για την καμπύλη Ed25519.
    y1x2 = (y1 * x2) % ED25519_P #Υπολογίζει το y1 * x2 mod p, που είναι επίσης μέρος του τύπου πρόσθεσης για την καμπύλη Ed25519.
    denominator_x = (1 + ED25519_D * x1x2 * y1y2) % ED25519_P #Υπολογίζει τον παρονομαστή για το x3, που είναι 1 + d * x1 * x2 * y1 * y2 mod p, όπου d είναι η σταθερά ED25519_D.
    denominator_y = (1 - ED25519_D * x1x2 * y1y2) % ED25519_P #Υπολογίζει τον παρονομαστή για το y3, που είναι 1 - d * x1 * x2 * y1 * y2 mod p.
    x3 = ((x1y2 + y1x2) * mod_inverse(denominator_x, ED25519_P)) % ED25519_P #Υπολογίζει το x3 χρησιμοποιώντας τον τύπο πρόσθεσης για την καμπύλη Ed25519: x3 = (x1 * y2 + y1 * x2) / (1 + d * x1 * x2 * y1 * y2) mod p. Η διαίρεση γίνεται με πολλαπλασιασμό με τον αντίστροφο του παρονομαστή.
    y3 = ((y1y2 - ED25519_A * x1x2) * mod_inverse(denominator_y, ED25519_P)) % ED25519_P #Υπολογίζει το y3 χρησιμοποιώντας τον τύπο πρόσθεσης για την καμπύλη Ed25519: y3 = (y1 * y2 - a * x1 * x2) / (1 - d * x1 * x2 * y1 * y2) mod p. Η διαίρεση γίνεται με πολλαπλασιασμό με τον αντίστροφο του παρονομαστή.
    return x3, y3


def _ed_ext_from_affine(point):
    x, y = point
    return x, y, 1, (x * y) % ED25519_P

def _ed_ext_add(P1, P2):
    X1,Y1,Z1,T1=P1; X2,Y2,Z2,T2=P2
    A=(Y1-X1)*(Y2-X2)%ED25519_P
    B=(Y1+X1)*(Y2+X2)%ED25519_P
    C=2*ED25519_D*T1*T2%ED25519_P
    D=2*Z1*Z2%ED25519_P
    E=(B-A)%ED25519_P; F=(D-C)%ED25519_P
    G=(D+C)%ED25519_P; H=(B+A)%ED25519_P
    return E*F%ED25519_P, G*H%ED25519_P, F*G%ED25519_P, E*H%ED25519_P

def _ed_ext_double(P1):
    X1,Y1,Z1,T1=P1
    A=X1*X1%ED25519_P; B=Y1*Y1%ED25519_P
    C=2*Z1*Z1%ED25519_P; D=(-A)%ED25519_P
    E=((X1+Y1)*(X1+Y1)-A-B)%ED25519_P
    G=(D+B)%ED25519_P; F=(G-C)%ED25519_P; H=(D-B)%ED25519_P
    return E*F%ED25519_P, G*H%ED25519_P, F*G%ED25519_P, E*H%ED25519_P

def _ed_ext_to_affine(Pt):
    X,Y,Z,T=Pt
    zi=pow(Z,-1,ED25519_P)
    return X*zi%ED25519_P, Y*zi%ED25519_P

def ed25519_scalar_mult(scalar, point):
    """Extended-coordinate scalar multiplication: one inversion at the end."""
    scalar %= ED25519_L
    result = None
    addend = _ed_ext_from_affine(point)
    while scalar:
        if scalar & 1:
            result = addend if result is None else _ed_ext_add(result, addend)
        addend = _ed_ext_double(addend)
        scalar >>= 1
    if result is None:
        return ED25519_IDENTITY
    return _ed_ext_to_affine(result)


def ed25519_encode_point(point):
    """Κωδικοποιεί ένα σημείο της καμπύλης Ed25519 σε bytes. Το x αποθηκεύεται στο πιο σημαντικό bit του τελευταίου byte, και το y στα υπόλοιπα 255 bits."""
    x, y = point #Unpacking το σημείο σε συντεταγμένες x και y.
    encoded = bytearray(y.to_bytes(32, "little")) #Κωδικοποιεί το y σε 32 bytes με little-endian μορφή και το αποθηκεύει σε ένα bytearray. Το y είναι το κύριο μέρος της κωδικοποίησης.
    encoded[31] |= (x & 1) << 7 #((x & 1) << 7)Το πιο σημαντικό bit του τελευταίου byte (byte 31) χρησιμοποιείται για να αποθηκεύσει το λιγότερο σημαντικό bit του x. Αυτό γίνεται με bitwise OR και bitwise AND για να θέσουμε το bit στο σωστό μέρος.
                                #το λιγότερο σημαντικό byte (LSB) είναι το πρώτο: encoded[0], και το πιο σημαντικό byte (MSB) είναι το τελευταίο: encoded[31]. Το x & 1 παίρνει το λιγότερο σημαντικό bit του x, και << 7 το μετακινεί στο πιο σημαντικό bit του τελευταίου byte.
    return bytes(encoded) #Επιστρέφει το κωδικοποιημένο σημείο ως bytes, έτοιμο για χρήση σε υπογραφές ή δημόσια κλειδιά.


def ed25519_clamp_scalar(h_bytes):
    """Παίρνει 32 bytes και τα “ρυθμίζει” (clamp) ώστε να γίνουν έγκυρο private scalar για Ed25519"""
    #Διασφαλίζουμε ότι ο private scalar έχει τη σωστή μορφή και είναι εντός των ασφαλών ορίων για χρήση στην καμπύλη Ed25519.
    scalar_bytes = bytearray(h_bytes[:32]) # Παίρνει τα πρώτα 32 bytes από το hash του seed και τα βάζει σε ένα bytearray για να μπορεί να τα τροποποιήσει.
    scalar_bytes[0] &= 248 #Το πρώτο byte (byte 0) έχει τα 3 λιγότερο σημαντικά bits μηδενισμένα (AND με 248, δηλαδή 11111000 σε δυαδική μορφή), για να διασφαλίσουμε ότι ο scalar είναι πολλαπλάσιο του 8.
    scalar_bytes[31] &= 63 #Το τελευταίο byte (byte 31) έχει τα 2 πιο σημαντικά bits μηδενισμένα (AND με 63, δηλαδή 00111111 σε δυαδική μορφή), για να διασφαλίσουμε ότι ο scalar είναι μικρότερος από 2^252.
    scalar_bytes[31] |= 64 #Το τελευταίο byte (byte 31) έχει το 6ο bit (bit 6) ρυθμισμένο σε 1 (OR με 64, δηλαδή 01000000 σε δυαδική μορφή), για να διασφαλίσουμε ότι ο scalar είναι τουλάχιστον 2^252.
    return int.from_bytes(scalar_bytes, "little") #Επιστρέφει τον clamped scalar ως ακέραιο, μετατρέποντας τα 32 bytes σε έναν ακέραιο με little-endian μορφή(το λιγότερο σημαντικό byte μπαίνει πρώτο).


def ed25519_keypair(seed):
    """ Δημιουργεί ένα ζεύγος κλειδιών (private scalar, prefix, public key) από έναν τυχαίο seed 32 bytes"""
    #nonce = είναι ένας προσωρινός μυστικός αριθμός,(μίας χρήσης) που χρησιμοποιείται μόνο για μία υπογραφή,
    hashed = hashlib.sha512(seed).digest() #Χρησιμοποιεί το SHA-512 hash function για να πάρει ένα 64-byte hash από τον seed. Τα πρώτα 32 bytes του hash θα χρησιμοποιηθούν για τον private scalar, και τα επόμενα 32 bytes θα χρησιμοποιηθούν ως prefix για τη δημιουργία του nonce κατά την υπογραφή. 
    private_scalar = ed25519_clamp_scalar(hashed) #Καλεί τη ed25519_clamp_scalar για να πάρει τον private scalar από τα πρώτα 32 bytes του hash, διασφαλίζοντας ότι είναι έγκυρος για χρήση στην καμπύλη Ed25519.
    prefix = hashed[32:] #Τα επόμενα 32 bytes του hash (bytes 32-63) χρησιμοποιούνται ως prefix για τη δημιουργία του nonce κατά την υπογραφή. Αυτό το prefix προσθέτει επιπλέον τυχαιότητα στη διαδικασία υπογραφής, καθώς ο nonce θα προκύπτει από το hash του prefix και του μηνύματος που υπογράφεται.
    public_key = ed25519_scalar_mult(private_scalar, ED25519_BASE_POINT) #Υπολογίζει το δημόσιο κλειδί πολλαπλασιάζοντας τον private scalar με το σημείο βάσης της καμπύλης Ed25519. Το αποτέλεσμα είναι ένα σημείο στην καμπύλη που αντιπροσωπεύει το δημόσιο κλειδί.

    return private_scalar, prefix, public_key #Επιστρέφει τον private scalar, το prefix και το δημόσιο κλειδί ως αποτέλεσμα της δημιουργίας του ζεύγους κλειδιών. Ο private scalar χρησιμοποιείται για την υπογραφή, το prefix χρησιμοποιείται για τη δημιουργία του nonce κατά την υπογραφή, και το public key χρησιμοποιείται για την επαλήθευση των υπογραφών που δημιουργούνται με τον αντίστοιχο private scalar.


def ed25519_verify(public_key, message, signature):
    """Επαληθεύει μια υπογραφή Ed25519 για ένα δεδομένο δημόσιο κλειδί και μήνυμα"""

    if len(signature) != 64: #Μια έγκυρη υπογραφή Ed25519 πρέπει να είναι ακριβώς 64 bytes.
        return False

    r_bytes = signature[:32] #Τα πρώτα 32 bytes της υπογραφής αντιπροσωπεύουν το R, το σημείο που προκύπτει από τον nonce κατά την υπογραφή. Αυτά τα bytes θα χρησιμοποιηθούν για να ανακατασκευάσουμε το σημείο R στην καμπύλη Ed25519 κατά την επαλήθευση.
    s_scalar = int.from_bytes(signature[32:], "little") #Τα επόμενα 32 bytes της υπογραφής αντιπροσωπεύουν το S, τον βαθμωτό που προκύπτει από τον nonce και τον private scalar κατά την υπογραφή. Αυτά τα bytes μετατρέπονται σε έναν ακέραιο με little-endian μορφή για να χρησιμοποιηθούν στην επαλήθευση της υπογραφής.
    if s_scalar >= ED25519_L:#Ο βαθμωτός S πρέπει να είναι μικρότερος από την τάξη της ομάδας (ED25519_L) για να είναι έγκυρη η υπογραφή. Αν το S είναι μεγαλύτερο ή ίσο με την τάξη, τότε η υπογραφή είναι άκυρη.
        return False

    r_y = int.from_bytes(r_bytes, "little") & ((1 << 255) - 1) #Το y του σημείου R ανακτάται από τα πρώτα 255 bits των r_bytes. Αυτό γίνεται με bitwise AND με (1 << 255) - 1, που είναι ένας αριθμός με τα πρώτα 255 bits σε 1 και το τελευταίο bit σε 0. Αυτό εξασφαλίζει ότι παίρνουμε μόνο τα πρώτα 255 bits για το y, και αγνοούμε το πιο σημαντικό bit που χρησιμοποιείται για να αποθηκεύσει το sign του x.
    r_sign = (r_bytes[31] >> 7) & 1 #Το sign του x(0,αν το x είναι άρτιο Ή 1 αν το x είναι περιττό) του σημείου R ανακτάται από το πιο σημαντικό bit του τελευταίου byte των r_bytes.
    a = (r_y * r_y - 1) % ED25519_P #Υπολογίζει το a για την εξίσωση της καμπύλης Ed25519, που είναι a = y² - 1 mod p. Αυτό είναι μέρος της διαδικασίας ανακατασκευής του σημείου R από το y και το sign του x.
    b = (ED25519_D * r_y * r_y + 1) % ED25519_P #Υπολογίζει το b για την εξίσωση της καμπύλης Ed25519, που είναι b = d * y² + 1 mod p, όπου d είναι η σταθερά ED25519_D. 
    x_square = (a * mod_inverse(b, ED25519_P)) % ED25519_P # Υπολογίζει το x² χρησιμοποιώντας την εξίσωση της καμπύλης Ed25519: -x² + y² = 1 + d * x² * y² mod p, που μπορεί να αναδιατυπωθεί ως x² = (y² - 1) / (d * y² + 1) mod p.
    x = pow(x_square, (ED25519_P + 3) // 8, ED25519_P) # Υπολογίζει το x χρησιμοποιώντας την εξίσωση της καμπύλης Ed25519. Για να βρούμε το x από το x², χρησιμοποιούμε τον αλγόριθμο για τετραγωνικές ρίζες στο πεδίο modulo p, που είναι pow(x_square, (p + 3) // 8, p) για p ≡ 5 (mod 8).

    if (x * x - x_square) % ED25519_P != 0:#Ελέγχει αν το x που υπολογίστηκε είναι πράγματι μια τετραγωνική ρίζα του x_square. Αν όχι, τότε πολλαπλασιάζει το x με pow(2, (p - 1) // 4, p) για να πάρει την άλλη τετραγωνική ρίζα, καθώς σε πεδία modulo p όπου p ≡ 5 (mod 8), υπάρχουν δύο τετραγωνικές ρίζες για κάθε μη μηδενικό στοιχείο.
        x = (x * pow(2, (ED25519_P - 1) // 4, ED25519_P)) % ED25519_P
    if x % 2 != r_sign: #Ελέγχει αν το sign του x που υπολογίστηκε ταιριάζει με το sign που ανακτήθηκε από τα r_bytes. Αν όχι, τότε παίρνει το αντίθετο του x (δηλαδή -x mod p) για να διασφαλίσει ότι το x έχει το σωστό sign.
        x = (-x) % ED25519_P #Τώρα έχουμε ανακατασκευάσει το σημείο R ως (x, r_y) με βάση τα r_bytes της υπογραφής. Αυτό το σημείο R θα χρησιμοποιηθεί στην επαλήθευση της υπογραφής.
    r_point = (x, r_y) #Το σημείο R που ανακατασκευάστηκε από τα r_bytes της υπογραφής, το οποίο θα χρησιμοποιηθεί στην επαλήθευση της υπογραφής. Το r_point είναι ένα σημείο στην καμπύλη Ed25519 που αντιπροσωπεύει το R που δημιουργήθηκε κατά την υπογραφή του μηνύματος.

    """Φτιάχνει έναν αριθμό k από το R, το public key και το μήνυμα.Αυτός ο αριθμός μπαίνει μετά στον έλεγχο της υπογραφής."""
    #k = H(R + A + M) mod l, όπου H είναι το hash function (SHA-512), R είναι το σημείο που προκύπτει από τον nonce κατά την υπογραφή, A είναι το δημόσιο κλειδί του υπογράφοντα, και M είναι το μήνυμα που υπογράφεται. Το αποτέλεσμα του hash μετατρέπεται σε έναν ακέραιο και μειώνεται modulo την τάξη της ομάδας (l) για να πάρουμε τον τελικό challenge που θα χρησιμοποιηθεί στην επαλήθευση της υπογραφής.
    k = int.from_bytes(hashlib.sha512(r_bytes + ed25519_encode_point(public_key) + message).digest(), "little") % ED25519_L 
    left = ed25519_scalar_mult(s_scalar, ED25519_BASE_POINT)#Υπολογίζει το αριστερό μέρος της εξίσωσης επαλήθευσης της υπογραφής Ed25519, που είναι S * B, όπου S είναι ο βαθμωτός που προκύπτει από την υπογραφή και B είναι το σημείο βάσης της καμπύλης Ed25519.
    right = ed25519_point_add(r_point, ed25519_scalar_mult(k, public_key)) #Υπολογίζει το δεξί μέρος της εξίσωσης επαλήθευσης της υπογραφής Ed25519, που είναι R + k * A, όπου R είναι το σημείο που προκύπτει από τον nonce κατά την υπογραφή, k είναι το κατακερματισμένο προθέσμιο (k = H(R || A || M) mod L), και A είναι το δημόσιο κλειδί του υπογράφοντα.

    return left == right #Ελέγχει αν το αριστερό μέρος της εξίσωσης επαλήθευσης (S * B) είναι ίσο με το δεξί μέρος (R + c * A). Αν είναι ίσα, τότε η υπογραφή είναι έγκυρη και επιστρέφει True.
# --- END OF ED25519 HELPERS ---

# --- ED25519 (Edwards-curve Digital Signature Algorithm) ---
def demo_ed25519(test_data=None):
    print("--- Ed25519 Demo ---\n")

    print("ΒΗΜΑ 1: Ορισμός Παραμέτρων Ed25519")
    print("-" * 50)
    print(f"Prime field p = 2^255 - 19 = {ED25519_P}") # Ο πρώτος αριθμός p που ορίζει το πεδίο modulo για την καμπύλη Ed25519 είναι 2^255 - 19, ένας μεγάλος πρώτος αριθμός που εξασφαλίζει την ασφάλεια της καμπύλης. Αυτός ο αριθμός χρησιμοποιείται για όλες τις πράξεις στην καμπύλη, όπως πρόσθεση σημείων και πολλαπλασιασμό σημείων, για να διασφαλιστεί ότι τα αποτελέσματα παραμένουν εντός του πεδίου.
    print(f"Group order l = {ED25519_L}") # Η τάξη της ομάδας l είναι ο αριθμός των στοιχείων στην ομάδα των σημείων της καμπύλης Ed25519. Η τάξη της ομάδας είναι σημαντική για την ασφάλεια της υπογραφής, καθώς καθορίζει το μέγεθος του χώρου των ιδιωτικών κλειδιών και την δυσκολία του προβλήματος του διακριτού λογαρίθμου στην καμπύλη.
    print(f"Base point B = ({ED25519_BASE_POINT[0]}, {ED25519_BASE_POINT[1]})\n") # Το σημείο βάσης B είναι ένα συγκεκριμένο σημείο στην καμπύλη Ed25519 που χρησιμοποιείται ως βάση για τις πράξεις πολλαπλασιασμού σημείων. Το δημόσιο κλειδί υπολογίζεται πολλαπλασιάζοντας τον ιδιωτικό scalar με αυτό το σημείο βάσης, και οι υπογραφές δημιουργούνται επίσης με βάση αυτό το σημείο. Η επιλογή ενός καλού σημείου βάσης είναι κρίσιμη για την ασφάλεια της καμπύλης.

    print("ΒΗΜΑ 2: Δημιουργία Κλειδιών")
    print("-" * 50)
    seed = hashlib.sha256(test_data.encode() if isinstance(test_data, str) else test_data).digest() if test_data else os.urandom(32)
    private_scalar, prefix, public_key = ed25519_keypair(seed)# Καλεί τη συνάρτηση ed25519_keypair με τον seed για να δημιουργήσει το ιδιωτικό scalar, το prefix και το δημόσιο κλειδί. Το ιδιωτικό scalar είναι ένας ακέραιος που χρησιμοποιείται για την υπογραφή, το prefix είναι ένα byte string που χρησιμοποιείται για τη δημιουργία του nonce κατά την υπογραφή, και το δημόσιο κλειδί είναι ένα σημείο στην καμπύλη που αντιπροσωπεύει το δημόσιο κλειδί του χρήστη.
    public_key_bytes = ed25519_encode_point(public_key)# Κωδικοποιεί το δημόσιο κλειδί σε bytes χρησιμοποιώντας τη συνάρτηση ed25519_encode_point, ώστε να μπορεί να χρησιμοποιηθεί στην υπογραφή και την επαλήθευση. Το δημόσιο κλειδί θα είναι 32 bytes, όπου τα πρώτα 255 bits αντιπροσωπεύουν το y του σημείου και το πιο σημαντικό bit του τελευταίου byte αντιπροσωπεύει το sign του x.
    print(f"Seed (32 bytes): {seed.hex()}") # Εκτυπώνει τον seed που χρησιμοποιήθηκε για τη δημιουργία του ζεύγους κλειδιών σε μορφή hex(123456(δεκαδικός)-->0x1E240). Αυτός ο seed είναι η βάση για την παραγωγή του ιδιωτικού scalar και του δημόσιου κλειδιού, και πρέπει να διατηρείται μυστικός για να διασφαλιστεί η ασφάλεια των κλειδιών.
    print(f"Private scalar a: {private_scalar}") # Εκτυπώνει τον ιδιωτικό scalar a που δημιουργήθηκε από τον seed. Αυτός ο scalar είναι το μυστικό κλειδί που θα χρησιμοποιηθεί για την υπογραφή μηνυμάτων. Πρέπει να διατηρείται μυστικός, καθώς οποιοσδήποτε έχει πρόσβαση σε αυτόν μπορεί να δημιουργήσει υπογραφές που φαίνονται να προέρχονται από τον κάτοχο του κλειδιού.
    print(f"Public key A: ({public_key[0]}, {public_key[1]})") # Εκτυπώνει το δημόσιο κλειδί σε μορφή συντεταγμένων (x, y) για να δείξει το σημείο στην καμπύλη που αντιπροσωπεύει το δημόσιο κλειδί. Το δημόσιο κλειδί είναι αυτό που θα χρησιμοποιηθεί για την επαλήθευση των υπογραφών που δημιουργούνται με τον αντίστοιχο ιδιωτικό scalar.
    print(f"Public key encoding: {public_key_bytes.hex()}\n") # Εκτυπώνει την κωδικοποιημένη μορφή του δημόσιου κλειδιού σε hex, που είναι η μορφή που θα χρησιμοποιηθεί στην υπογραφή και την επαλήθευση. Αυτή η μορφή περιλαμβάνει το y του σημείου και το sign του x, και είναι η τυπική μορφή για τα δημόσια κλειδιά Ed25519.

    print("ΒΗΜΑ 3: Υπογραφή Μηνύματος")
    print("-" * 50)
    message = test_data.encode() if isinstance(test_data, str) else test_data #Το μήνυμα που θα υπογραφεί. Αν το test_data είναι string, το κωδικοποιεί σε bytes, αλλιώς το χρησιμοποιεί όπως είναι. Το μήνυμα μπορεί να είναι οποιοδήποτε byte string, και η υπογραφή θα εξαρτηθεί από το περιεχόμενο του μηνύματος, καθώς ο nonce που χρησιμοποιείται για την υπογραφή δημιουργείται από το hash του prefix και του μηνύματος.
    print(f"Μήνυμα: {message[:50].decode(errors='ignore')}") # Το μήνυμα προέρχεται από το dataset ώστε να αλλάζει με το input.
    nonce = int.from_bytes(hashlib.sha512(prefix + message).digest(), "little") % ED25519_L # Δημιουργεί έναν nonce για την υπογραφή, ο οποίος είναι ένας προσωρινός μυστικός αριθμός που χρησιμοποιείται μόνο για μία υπογραφή. Ο nonce δημιουργείται από το hash του prefix (που προήλθε από τον seed) και του μηνύματος που υπογράφεται, για να προσθέσει επιπλέον τυχαιότητα στη διαδικασία υπογραφής. Το αποτέλεσμα του hash μετατρέπεται σε έναν ακέραιο και μειώνεται modulo την τάξη της ομάδας (ED25519_L) για να διασφαλίσει ότι ο nonce είναι εντός των ασφαλών ορίων για χρήση στην καμπύλη Ed25519.
    r_point = ed25519_scalar_mult(nonce, ED25519_BASE_POINT) # Υπολογίζει το σημείο R πολλαπλασιάζοντας τον nonce με το σημείο βάσης της καμπύλης Ed25519. Το αποτέλεσμα είναι ένα σημείο στην καμπύλη που θα χρησιμοποιηθεί για να υπολογίσουμε το r και θα είναι μέρος της υπογραφής.
    r_bytes = ed25519_encode_point(r_point) # Κωδικοποιεί το σημείο R σε bytes χρησιμοποιώντας τη συνάρτηση ed25519_encode_point, ώστε να μπορεί να χρησιμοποιηθεί στην υπογραφή και την επαλήθευση. Το r_bytes θα είναι 32 bytes, όπου τα πρώτα 255 bits αντιπροσωπεύουν το y του σημείου R και το πιο σημαντικό bit του τελευταίου byte αντιπροσωπεύει το sign του x του σημείου R.
    k = int.from_bytes(hashlib.sha512(r_bytes + public_key_bytes + message).digest(), "little") % ED25519_L # k = H(R || A || M) mod L (RFC 8032): Υπολογίζει το κατακερματισμένο προθέσμιο k, που είναι ένας ακέραιος που υπολογίζεται από το hash των r_bytes (R), public_key_bytes (A) και message (M). Το αποτέλεσμα μετατρέπεται σε έναν ακέραιο και μειώνεται modulo την τάξη της ομάδας (ED25519_L) για να διασφαλίσει ότι το k είναι εντός των ασφαλών ορίων.
    s = (nonce + k * private_scalar) % ED25519_L # Υπολογίζει το s που είναι μέρος της υπογραφής. Το s υπολογίζεται ως το nonce πρόσθεση του challenge επί του private_scalar, μετά από modulo την τάξη της ομάδας (ED25519_L).
    signature = r_bytes + s.to_bytes(32, "little") # Δημιουργεί την υπογραφή συνδυάζοντας τα r_bytes και s. Τo signature είναι 64 bytes, όπου τα πρώτα 32 bits αντιπροσωπεύουν τo r_bytes και τo επόμενo 32 bits αντιπροσωπεύουν τo s.
    print(f"Nonce r: {nonce}")
    print(f"R = r * B: ({r_point[0]}, {r_point[1]})")
    print(f"k = H(R || A || M) mod L: {k}")
    print(f"Signature S = (r + k*a) mod L: {s}")
    print(f"Signature (hex): {signature.hex()}\n")

    print("ΒΗΜΑ 4: Επαλήθευση Υπογραφής")
    print("-" * 50)
    valid = ed25519_verify(public_key, message, signature) # Καλεί τη συνάρτηση ed25519_verify με το δημόσιο κλειδί, το μήνυμα και την υπογραφή για να επαληθεύσει αν η υπογραφή είναι έγκυρη. Η συνάρτηση θα επιστρέψει True αν η υπογραφή είναι έγκυρη και False αν είναι άκυρη.
    if valid:
        print("✓ ΕΠΑΛΗΘΕΥΣΗ ΕΠΙΤΥΧΗΣ: Η Ed25519 υπογραφή είναι έγκυρη!\n")
    else:
        print("✗ ΕΠΑΛΗΘΕΥΣΗ ΑΠΟΤΥΧΗΣ: Η Ed25519 υπογραφή είναι άκυρη!\n")


# --- ECDSA (Elliptic Curve Digital Signature Algorithm) ---
def demo_ecdsa(test_data=None):
    print("--- ECDSA (secp256k1) ---\n")
    message = test_data.encode() if isinstance(test_data, str) else (test_data or b"")
    private_key, public_key = ecdsa_keypair()
    digest = hashlib.sha256(message).digest()
    signature = ecdsa_sign_digest(private_key, digest)
    valid = ecdsa_verify_digest(public_key, digest, signature)
    print("Curve: secp256k1")
    print(f"Field size: {SECP256K1_P.bit_length()} bits")
    print(f"Public key (compressed): {secp256k1_encode_compressed(public_key).hex()}")
    print(f"Signature (r||s): {signature[0]:064x}{signature[1]:064x}")
    print(f"Verification: {valid}\n")



# ===== Standard-size parameters / pure Python crypto primitives =====
SECP256K1_P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
SECP256K1_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
SECP256K1_G = (
    55066263022277343669578718895168534326250603453777594175500187360389116729240,
    32670510020758816978083085130507043184471273380659243275938904335757337482424,
)

def _secp_double(Pt):
    if Pt is None: return None
    X,Y,Z=Pt
    if Y==0: return None
    S=4*X*Y*Y%SECP256K1_P
    M=3*X*X%SECP256K1_P
    X3=(M*M-2*S)%SECP256K1_P
    Y3=(M*(S-X3)-8*pow(Y,4,SECP256K1_P))%SECP256K1_P
    Z3=2*Y*Z%SECP256K1_P
    return X3,Y3,Z3

def _secp_add(P1,P2):
    if P1 is None:return P2
    if P2 is None:return P1
    X1,Y1,Z1=P1; X2,Y2,Z2=P2
    z1z1=Z1*Z1%SECP256K1_P; z2z2=Z2*Z2%SECP256K1_P
    u1=X1*z2z2%SECP256K1_P; u2=X2*z1z1%SECP256K1_P
    s1=Y1*Z2*z2z2%SECP256K1_P; s2=Y2*Z1*z1z1%SECP256K1_P
    if u1==u2:
        return _secp_double(P1) if s1==s2 else None
    H=(u2-u1)%SECP256K1_P; I=(2*H)**2%SECP256K1_P; J=H*I%SECP256K1_P
    r=2*(s2-s1)%SECP256K1_P; V=u1*I%SECP256K1_P
    X3=(r*r-J-2*V)%SECP256K1_P
    Y3=(r*(V-X3)-2*s1*J)%SECP256K1_P
    Z3=((Z1+Z2)**2-z1z1-z2z2)*H%SECP256K1_P
    return X3,Y3,Z3

def secp256k1_scalar_mult(k, point=SECP256K1_G):
    k%=SECP256K1_N
    result=None; addend=(point[0],point[1],1)
    while k:
        if k&1: result=_secp_add(result,addend)
        addend=_secp_double(addend); k>>=1
    if result is None:return None
    X,Y,Z=result; zi=pow(Z,-1,SECP256K1_P); z2=zi*zi%SECP256K1_P
    return X*z2%SECP256K1_P, Y*z2*zi%SECP256K1_P

def secp256k1_encode_compressed(point):
    x,y=point
    return bytes([2|(y&1)])+x.to_bytes(32,"big")

def _rfc6979_k(private_key,digest,q=SECP256K1_N):
    rolen=(q.bit_length()+7)//8
    bx=private_key.to_bytes(rolen,"big")
    z=int.from_bytes(digest,"big")%q
    bh=z.to_bytes(rolen,"big")
    V=b"\x01"*32; K=b"\x00"*32
    K=hmac.new(K,V+b"\x00"+bx+bh,hashlib.sha256).digest()
    V=hmac.new(K,V,hashlib.sha256).digest()
    K=hmac.new(K,V+b"\x01"+bx+bh,hashlib.sha256).digest()
    V=hmac.new(K,V,hashlib.sha256).digest()
    while True:
        T=b""
        while len(T)<rolen:
            V=hmac.new(K,V,hashlib.sha256).digest(); T+=V
        k=int.from_bytes(T[:rolen],"big")
        if 1<=k<q:return k
        K=hmac.new(K,V+b"\x00",hashlib.sha256).digest()
        V=hmac.new(K,V,hashlib.sha256).digest()

def ecdsa_keypair():
    d=secrets.randbelow(SECP256K1_N-1)+1
    return d,secp256k1_scalar_mult(d)

def ecdsa_sign_digest(private_key,digest):
    z=int.from_bytes(digest,"big")%SECP256K1_N
    k=_rfc6979_k(private_key,digest)
    R=secp256k1_scalar_mult(k); r=R[0]%SECP256K1_N
    if r==0: raise RuntimeError("ECDSA r=0")
    s=pow(k,-1,SECP256K1_N)*(z+r*private_key)%SECP256K1_N
    if s==0: raise RuntimeError("ECDSA s=0")
    if s>SECP256K1_N//2:s=SECP256K1_N-s
    return r,s

def ecdsa_verify_digest(public_key,digest,signature):
    r,s=signature
    if not(1<=r<SECP256K1_N and 1<=s<=SECP256K1_N//2):return False
    z=int.from_bytes(digest,"big")%SECP256K1_N
    w=pow(s,-1,SECP256K1_N); u1=z*w%SECP256K1_N; u2=r*w%SECP256K1_N
    P1=secp256k1_scalar_mult(u1); P2=secp256k1_scalar_mult(u2,public_key)
    J=_secp_add(None if P1 is None else (P1[0],P1[1],1),
                None if P2 is None else (P2[0],P2[1],1))
    if J is None:return False
    X,Y,Z=J; zi=pow(Z,-1,SECP256K1_P)
    return (X*zi*zi%SECP256K1_P)%SECP256K1_N==r

DH_GROUP14_P=int("""
FFFFFFFF FFFFFFFF C90FDAA2 2168C234 C4C6628B 80DC1CD1
29024E08 8A67CC74 020BBEA6 3B139B22 514A0879 8E3404DD
EF9519B3 CD3A431B 302B0A6D F25F1437 4FE1356D 6D51C245
E485B576 625E7EC6 F44C42E9 A637ED6B 0BFF5CB6 F406B7ED
EE386BFB 5A899FA5 AE9F2411 7C4B1FE6 49286651 ECE45B3D
C2007CB8 A163BF05 98DA4836 1C55D39A 69163FA8 FD24CF5F
83655D23 DCA3AD96 1C62F356 208552BB 9ED52907 7096966D
670C354E 4ABC9804 F1746C08 CA18217C 32905E46 2E36CE3B
E39E772C 180E8603 9B2783A2 EC07A28F B5C55DF0 6F4C52C9
DE2BCBF6 95581718 3995497C EA956AE5 15D22618 98FA0510
15728E5A 8AACAA68 FFFFFFFF FFFFFFFF
""".replace("\n","").replace(" ",""),16)

# DSA 2048/256 domain parameters from RFC 6979 Appendix A.2.2.
DSA_P=int("""
9DB6FB5951B66BB6FE1E140F1D2CE5502374161FD6538DF1648218642F0B5C48
C8F7A41AADFA187324B87674FA1822B00F1ECF8136943D7C55757264E5A1A44F
FE012E9936E00C1D3E9310B01C7D179805D3058B2A9F4BB6F9716BFE6117C6B5
B3CC4D9BE341104AD4A80AD6C94E005F4B993E14F091EB51743BF33050C38DE2
35567E1B34C3D6A5C0CEAA1A0F368213C3D19843D0B4B09DCB9FC72D39C8DE41
F1BF14D4BB4563CA28371621CAD3324B6A2D392145BEBFAC748805236F5CA2FE
92B871CD8F9C36D3292B5509CA8CAA77A2ADFC7BFD77DDA6F71125A7456FEA15
3E433256A2261C6A06ED3693797E7995FAD5AABBCFBE3EDA2741E375404AE25B
""".replace("\n",""),16)
DSA_Q=int("F2C3119374CE76C9356990B465374A17F23F9ED35089BD969F61C6DDE9998C1F",16)
DSA_G=int("""
5C7FF6B06F8F143FE8288433493E4769C4D988ACE5BE25A0E24809670716C613
D7B0CEE6932F8FAA7C44D2CB24523DA53FBE4F6EC3595892D1AA58C4328A06C4
6A15662E7EAA703A1DECF8BBB2D05DBE2EB956C142A338661D10461C0D135472
085057F3494309FFA73C611F78B32ADBB5740C361C9F35BE90997DB2014E2EF5
AA61782F52ABEB8BD6432C4DD097BC5423B285DAFB60DC364E8161F4A2A35ACA
3A10B1C4D203CC76A470A33AFDCBDD92959859ABD8B56E1725252D78EAC66E71
BA9AE3F1DD2487199874393CD4D832186800654760E1E34C09E4D155179F9EC0
DC4473F996BDCE6EED1CABED8B6F116F7AD9CF505DF0F998E34AB27514B0FFE7
""".replace("\n",""),16)

def _rfc6979_dsa_k(x,digest):
    rolen=32; bx=x.to_bytes(rolen,"big"); bh=(int.from_bytes(digest,"big")%DSA_Q).to_bytes(rolen,"big")
    V=b"\x01"*32; K=b"\x00"*32
    K=hmac.new(K,V+b"\x00"+bx+bh,hashlib.sha256).digest(); V=hmac.new(K,V,hashlib.sha256).digest()
    K=hmac.new(K,V+b"\x01"+bx+bh,hashlib.sha256).digest(); V=hmac.new(K,V,hashlib.sha256).digest()
    while True:
        V=hmac.new(K,V,hashlib.sha256).digest(); k=int.from_bytes(V,"big")
        if 1<=k<DSA_Q:return k
        K=hmac.new(K,V+b"\x00",hashlib.sha256).digest(); V=hmac.new(K,V,hashlib.sha256).digest()

def dsa_sign_digest(x,h,digest):
    k=_rfc6979_dsa_k(x,digest); r=pow(DSA_G,k,DSA_P)%DSA_Q
    s=pow(k,-1,DSA_Q)*(h+x*r)%DSA_Q
    return r,s

def dsa_verify_digest(y,h,r,s):
    if not(0<r<DSA_Q and 0<s<DSA_Q):return False
    w=pow(s,-1,DSA_Q)
    v=((pow(DSA_G,h*w%DSA_Q,DSA_P)*pow(y,r*w%DSA_Q,DSA_P))%DSA_P)%DSA_Q
    return v==r

def _is_probable_prime(n,rounds=16):
    if n<2:return False
    for p in (2,3,5,7,11,13,17,19,23,29,31,37):
        if n%p==0:return n==p
    d=n-1;s=0
    while d%2==0:s+=1;d//=2
    for _ in range(rounds):
        a=secrets.randbelow(n-3)+2;x=pow(a,d,n)
        if x in(1,n-1):continue
        for _ in range(s-1):
            x=x*x%n
            if x==n-1:break
        else:return False
    return True

def _generate_prime(bits):
    while True:
        c=secrets.randbits(bits)|(1<<(bits-1))|1
        if _is_probable_prime(c):return c

def rsa_generate_keypair(bits=2048):
    e=65537
    while True:
        p=_generate_prime(bits//2);q=_generate_prime(bits//2)
        if p==q:continue
        phi=(p-1)*(q-1)
        if gcd(e,phi)==1:return (p*q,pow(e,-1,phi)),(p*q,e)

SHA256_DIGESTINFO_PREFIX=bytes.fromhex("3031300d060960864801650304020105000420")
def rsa_emsa_pkcs1_v1_5_encode(digest,k):
    T=SHA256_DIGESTINFO_PREFIX+digest
    return b"\x00\x01"+b"\xff"*(k-len(T)-3)+b"\x00"+T

def rsa_sign_pkcs1_v15(private_key,digest):
    n,d=private_key;k=(n.bit_length()+7)//8;em=rsa_emsa_pkcs1_v1_5_encode(digest,k)
    return pow(int.from_bytes(em,"big"),d,n).to_bytes(k,"big")

def rsa_verify_pkcs1_v15(public_key,digest,signature):
    n,e=public_key;k=(n.bit_length()+7)//8
    if len(signature)!=k:return False
    em=pow(int.from_bytes(signature,"big"),e,n).to_bytes(k,"big")
    return em==rsa_emsa_pkcs1_v1_5_encode(digest,k)

# --- RSA (Encryption/Decryption) --- This algorithm can be used for encryption,signatures,key exchange
def demo_rsa(test_data=None):
    print("--- RSA-2048 Demo ---")
    private_key, public_key = rsa_generate_keypair(2048)
    message = test_data.encode() if isinstance(test_data, str) else (test_data or b"")
    digest = hashlib.sha256(message).digest()
    signature = rsa_sign_pkcs1_v15(private_key, digest)
    valid = rsa_verify_pkcs1_v15(public_key, digest, signature)
    print(f"Modulus: {public_key[0].bit_length()} bits")
    print(f"Signature size: {len(signature)} bytes")
    print(f"Verification: {valid}\n")


# --- DIFFIE-HELLMAN (Key Exchange) --- Alice & Bob Example --- Used only for Encryption, not for signatures & key exchange
#Shared Secret over an unsecured medium...then shared secret is used to generate a symmetric key for encryption.
def demo_diffie_hellman(test_data=None):
    print("--- Diffie-Hellman (RFC 3526 Group 14) ---")
    p = DH_GROUP14_P; g = 2
    a_priv = secrets.randbits(256); b_priv = secrets.randbits(256)
    a_pub = pow(g, a_priv, p); b_pub = pow(g, b_priv, p)
    secret_a = pow(b_pub, a_priv, p); secret_b = pow(a_pub, b_priv, p)
    print(f"Modulus: {p.bit_length()} bits")
    print(f"Shared secret matches: {secret_a == secret_b}\n")


# --- DSA (Digital Signature) --- Used only for signatures, not for encryption & key exchange
def demo_dsa(test_data=None):
    print("--- DSA-2048/256 Demo ---")
    message = test_data.encode() if isinstance(test_data, str) else (test_data or b"")
    x = secrets.randbelow(DSA_Q - 1) + 1
    y = pow(DSA_G, x, DSA_P)
    digest = hashlib.sha256(message).digest()
    h = int.from_bytes(digest, "big") % DSA_Q
    r, s = dsa_sign_digest(x, h, digest)
    valid = dsa_verify_digest(y, h, r, s)
    print(f"p: {DSA_P.bit_length()} bits, q: {DSA_Q.bit_length()} bits")
    print("Public key size: 256 bytes")
    print("Signature size: 64 bytes")
    print(f"Verification: {valid}\n")



### Helper Functions για τον υπολογισμό κάθε μετρικής για κάθε σενάριο υλοποίησης αλγορίθμων.
#Calculate key_gen_speed,latency_verification,latency_signing,key_size,signature_size and valid(T or F ,if the signature is valid)
def measure_ed25519_metrics(message_bytes):
    # Key generation
    t0 = time.perf_counter_ns()
    seed = os.urandom(32)
    private_scalar, prefix, public_key = ed25519_keypair(seed)
    keygen_ms = (time.perf_counter_ns() - t0) / 1_000_000

    # Signing
    t0 = time.perf_counter_ns()
    nonce = int.from_bytes(hashlib.sha512(prefix + message_bytes).digest(), "little") % ED25519_L
    r_point = ed25519_scalar_mult(nonce, ED25519_BASE_POINT)
    r_bytes = ed25519_encode_point(r_point)
    k = int.from_bytes(hashlib.sha512(r_bytes + ed25519_encode_point(public_key) + message_bytes).digest(), "little") % ED25519_L
    s = (nonce + k * private_scalar) % ED25519_L
    signature = r_bytes + s.to_bytes(32, "little")
    sign_ms = (time.perf_counter_ns() - t0) / 1_000_000

    # Verification
    t0 = time.perf_counter_ns()
    valid = ed25519_verify(public_key, message_bytes, signature)
    verify_ms = (time.perf_counter_ns() - t0) / 1_000_000

    key_size = len(ed25519_encode_point(public_key))
    sig_size = len(signature)
    return keygen_ms, sign_ms, verify_ms, key_size, sig_size, valid


def measure_ecdsa_metrics(message_bytes):
    t0 = time.perf_counter_ns()
    private_key, public_key = ecdsa_keypair()
    keygen_ms = (time.perf_counter_ns() - t0) / 1_000_000
    t0 = time.perf_counter_ns()
    digest = hashlib.sha256(message_bytes).digest()
    signature = ecdsa_sign_digest(private_key, digest)
    sign_ms = (time.perf_counter_ns() - t0) / 1_000_000
    t0 = time.perf_counter_ns()
    verified = ecdsa_verify_digest(public_key, digest, signature)
    verify_ms = (time.perf_counter_ns() - t0) / 1_000_000
    return keygen_ms, sign_ms, verify_ms, 33, 64, verified


def measure_dsa_metrics(message_bytes):
    t0 = time.perf_counter_ns()
    x = secrets.randbelow(DSA_Q - 1) + 1
    y = pow(DSA_G, x, DSA_P)
    keygen_ms = (time.perf_counter_ns() - t0) / 1_000_000
    t0 = time.perf_counter_ns()
    digest = hashlib.sha256(message_bytes).digest()
    h = int.from_bytes(digest, "big") % DSA_Q
    r, s = dsa_sign_digest(x, h, digest)
    sign_ms = (time.perf_counter_ns() - t0) / 1_000_000
    t0 = time.perf_counter_ns()
    verified = dsa_verify_digest(y, h, r, s)
    verify_ms = (time.perf_counter_ns() - t0) / 1_000_000
    return keygen_ms, sign_ms, verify_ms, 256, 64, verified


def measure_rsa_metrics(message_bytes):
    t0 = time.perf_counter_ns()
    private_key, public_key = rsa_generate_keypair(2048)
    keygen_ms = (time.perf_counter_ns() - t0) / 1_000_000
    digest = hashlib.sha256(message_bytes).digest()
    t0 = time.perf_counter_ns()
    signature = rsa_sign_pkcs1_v15(private_key, digest)
    sign_ms = (time.perf_counter_ns() - t0) / 1_000_000
    t0 = time.perf_counter_ns()
    verified = rsa_verify_pkcs1_v15(public_key, digest, signature)
    verify_ms = (time.perf_counter_ns() - t0) / 1_000_000
    return keygen_ms, sign_ms, verify_ms, 259, 256, verified

def measure_diffie_hellman_metrics(message_bytes):
    p = DH_GROUP14_P; g = 2
    t0 = time.perf_counter_ns()
    a_priv = secrets.randbits(256); b_priv = secrets.randbits(256)
    a_pub = pow(g, a_priv, p); b_pub = pow(g, b_priv, p)
    keygen_ms = (time.perf_counter_ns() - t0) / 1_000_000
    t0 = time.perf_counter_ns()
    secret_a = pow(b_pub, a_priv, p)
    sign_ms = (time.perf_counter_ns() - t0) / 1_000_000
    t0 = time.perf_counter_ns()
    secret_b = pow(a_pub, b_priv, p)
    verify_ms = (time.perf_counter_ns() - t0) / 1_000_000
    return keygen_ms, sign_ms, verify_ms, 256, None, secret_a == secret_b



if __name__ == "__main__":
    # Δημιουργία dataset με τα 4 διαφορετικά μεγέθη (ο generator θα δημιουργήσει τυχαίο seed)
    dataset = generate_dataset()
    
    #Debuging στο terminal με τιμές παραμετρων και κρυπτογράφιση-αποκρυπτογράφηση μηνυμάτων σε κάθε σενάριο
    print("=" * 60)
    print("ΣΤΑΤΙΣΤΙΚΑ DATASET")
    print("=" * 60)
    for size, text in dataset.items():
        print(f"• {size:>7,} χαρακτήρες: {len(text):>7,} bytes")
        print(f"           Πρώτοι 50 χαρακτήρες: {text[:50]}...")
        print()
    
    print("=" * 60)
    print("ΔΟΚΙΜΗ ΑΛΓΟΡΙΘΜΩΝ ΓΙΑ ΚΑΘΕ ΜΕΓΕΘΟΣ DATASET")
    print("=" * 60 + "\n")
    
    # Αρχικοποίηση metrics collector
    metrics = MetricsCollector()
    
    #Δοκιμή για κάθε μέγεθος dataset,εδώ υπολογίζω, latency(runtime), throughput(διαφορετικά inputs),key_gen_speed,latency_verification,latency_signing,key_size,signature_size
    # για κάθε αλγόριθμο και αποθηκεύω τα αποτελέσματα στο metrics collector για να τα εξάγω μετά σε Excel.
    #Το latency μετριέται σε milliseconds (ms) και το throughput σε kilobytes per second (KB/s).
    for size in [1000, 10000, 100000, 1000000]:
        test_text = dataset[size]
        input_size_kb = size / 1024
        
        print(f"\n{'='*60}")
        print(f"ΔΟΚΙΜΗ ΜΕ DATASET {size:,} ΧΑΡΑΚΤΗΡΩΝ ({input_size_kb:.1f} KB)")
        print(f"{'='*60}\n")
        
        # RSA
        print("▶ RSA...")
        demo_rsa(test_text) # Εκτελεί το demo για το RSA με το συγκεκριμένο test_text. Αυτό θα εμφανίσει τα βήματα της διαδικασίας κρυπτογράφησης και αποκρυπτογράφησης, καθώς και τα αποτελέσματα.
        kg_ms, sign_ms, ver_ms, key_size, sig_size, verified = measure_rsa_metrics(test_text.encode() if isinstance(test_text, str) else test_text)
        throughput = (input_size_kb / 1024) / (max(sign_ms, 0.001) / 1000) 
        metrics.add_metric('RSA', f'{size:,}', kg_ms, sign_ms, ver_ms, throughput, key_size, sig_size)

        # Diffie-Hellman
        print("▶ Diffie-Hellman...")
        demo_diffie_hellman(test_text) # Εκτελεί το demo για το Diffie-Hellman με το συγκεκριμένο test_text. Αυτό θα εμφανίσει τα βήματα της διαδικασίας κρυπτογράφησης και αποκρυπτογράφησης, καθώς και τα αποτελέσματα.
        kg_ms, sign_ms, ver_ms, key_size, sig_size, verified = measure_diffie_hellman_metrics(test_text.encode() if isinstance(test_text, str) else test_text)
        throughput = (input_size_kb / 1024) / (max(sign_ms, 0.001) / 1000) 
        metrics.add_metric('Diffie-Hellman', f'{size:,}', kg_ms, sign_ms, ver_ms, throughput, key_size, sig_size)

        # DSA
        print("▶ DSA...")
        demo_dsa(test_text) # Εκτελεί το demo για το DSA με το συγκεκριμένο test_text. Αυτό θα εμφανίσει τα βήματα της διαδικασίας κρυπτογράφησης και αποκρυπτογράφησης, καθώς και τα αποτελέσματα.
        kg_ms, sign_ms, ver_ms, key_size, sig_size, verified = measure_dsa_metrics(test_text.encode() if isinstance(test_text, str) else test_text)
        throughput = (input_size_kb / 1024) / (max(sign_ms, 0.001) / 1000) 
        metrics.add_metric('DSA', f'{size:,}', kg_ms, sign_ms, ver_ms, throughput, key_size, sig_size)

        # ECDSA
        print("▶ ECDSA...")
        demo_ecdsa(test_text) # Εκτελεί το demo για το ECDSA με το συγκεκριμένο test_text. Αυτό θα εμφανίσει τα βήματα της διαδικασίας κρυπτογράφησης και αποκρυπτογράφησης, καθώς και τα αποτελέσματα.
        kg_ms, sign_ms, ver_ms, key_size, sig_size, verified = measure_ecdsa_metrics(test_text.encode() if isinstance(test_text, str) else test_text)
        throughput = (input_size_kb / 1024) / (max(sign_ms, 0.001) / 1000) 
        metrics.add_metric('ECDSA', f'{size:,}', kg_ms, sign_ms, ver_ms, throughput, key_size, sig_size)

        # Ed25519
        print("▶ Ed25519...")
        demo_ed25519(test_text) # Εκτελεί το demo για το Ed25519 με το συγκεκριμένο test_text. Αυτό θα εμφανίσει τα βήματα της διαδικασίας κρυπτογράφησης και αποκρυπτογράφησης, καθώς και τα αποτελέσματα.
        kg_ms, sign_ms, ver_ms, key_size, sig_size, verified = measure_ed25519_metrics(test_text.encode() if isinstance(test_text, str) else test_text)
        throughput = (input_size_kb / 1024) / (max(sign_ms, 0.001) / 1000) 
        metrics.add_metric('Ed25519', f'{size:,}', kg_ms, sign_ms, ver_ms, throughput, key_size, sig_size)
    
    # Εξαγωγή σε Excel
    print("\n" + "=" * 60)
    metrics.export_to_excel('cryptography_metrics_realistic.xlsx')
    
    # Δημιουργία διαγραμμάτων με matplotlib  
    create_plots(metrics, outdir='plots')
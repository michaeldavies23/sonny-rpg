import streamlit as st
import pandas as pd
import os
import random
import math

# ==========================================
# ⚙️ CONFIG & STYLE
# ==========================================
st.set_page_config(page_title="Sonny's Infinite RPG", page_icon="♾️", layout="centered")
DATA_FILE = "sonny_save_infinite.csv"

st.markdown("""
<style>
    .stApp { background-color: #0e0e16; color: white; }
    
    /* PRESTIGE BADGE */
    .prestige-badge {
        background: linear-gradient(45deg, #FF512F, #DD2476);
        padding: 5px 15px; border-radius: 15px; font-weight: bold;
        box-shadow: 0 0 10px #FF512F;
    }

    /* CARD STYLES */
    .monster-card {
        background-color: #1f1f2e; border: 2px solid #333;
        border-radius: 15px; padding: 20px; text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.6);
    }
    .big-emoji { font-size: 90px; margin: 0; line-height: 1.0; }
    
    /* SHOP GRID */
    .shop-grid { display: flex; flex-wrap: wrap; gap: 10px; justify-content: center; }
    
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 🧠 THE INFINITE MATHS ENGINE
# ==========================================
class MathEngine:
    @staticmethod
    def generate():
        """Generates a random Year 6 SATs Arithmetic Question"""
        q_type = random.choice(['add', 'sub', 'mult', 'div', 'sq', 'dec_add', 'fraction'])
        
        if q_type == 'add':
            a = random.randint(100, 9999)
            b = random.randint(100, 9999)
            return {"type": "maths", "text": f"{a} + {b} = ?", "ans": str(a+b), "hint": "Column addition."}
            
        elif q_type == 'sub':
            a = random.randint(500, 9999)
            b = random.randint(10, a) # Ensure result is positive
            return {"type": "maths", "text": f"{a} - {b} = ?", "ans": str(a-b), "hint": "Column subtraction."}
            
        elif q_type == 'mult':
            # Mix of times tables and long multiplication
            if random.random() > 0.5:
                a = random.randint(2, 12)
                b = random.randint(2, 12)
            else:
                a = random.randint(12, 99)
                b = random.randint(2, 9)
            return {"type": "maths", "text": f"{a} x {b} = ?", "ans": str(a*b), "hint": "Partition or grid method."}
            
        elif q_type == 'div':
            # Reverse multiplication to ensure whole numbers
            ans = random.randint(2, 12)
            b = random.randint(2, 12)
            a = ans * b
            return {"type": "maths", "text": f"{a} ÷ {b} = ?", "ans": str(ans), "hint": f"{b} times what equals {a}?"}
            
        elif q_type == 'sq':
            a = random.randint(2, 12)
            return {"type": "maths", "text": f"{a}² (Squared)", "ans": str(a*a), "hint": f"{a} x {a}"}
            
        elif q_type == 'dec_add':
            a = round(random.uniform(1, 10), 1)
            b = round(random.uniform(1, 10), 1)
            ans = "{:.1f}".format(a+b)
            return {"type": "maths", "text": f"{a} + {b} = ?", "ans": ans, "hint": "Line up the dots."}
        
        elif q_type == 'fraction':
            # Simple fractions to decimals
            pairs = [("1/2", "0.5"), ("1/4", "0.25"), ("3/4", "0.75"), ("1/10", "0.1"), ("1/5", "0.2")]
            q, a = random.choice(pairs)
            return {"type": "maths", "text": f"{q} as a decimal?", "ans": a, "hint": "Common conversion."}

        return {"type": "maths", "text": "10 + 10", "ans": "20", "hint": "Easy one."}

# ==========================================
# 📚 STATIC CONTENT (Spelling/Reading)
# ==========================================
# Expanded list - 50+ words
SPELLING_BANK = [
    ("accommodate", "Double C, Double M"), ("accompany", "Double C"), ("achieve", "i before e"),
    ("aggressive", "Double G, Double S"), ("amateur", "Ends in -eur"), ("ancient", "ci sounds like sh"),
    ("apparent", "Double P"), ("appreciate", "Double P"), ("attached", "Double T"),
    ("available", "ai in the middle"), ("average", "v-e-r"), ("awkward", "w-k-w"),
    ("bargain", "gain at the end"), ("bruise", "u before i"), ("category", "cat-E-gory"),
    ("cemetery", "Three e's"), ("committee", "Double M, T, and E"), ("communicate", "Double M"),
    ("community", "Double M"), ("competition", "pet in the middle"), ("conscience", "sci-ence"),
    ("conscious", "sci-ous"), ("controversy", "ro-ver"), ("convenience", "veni-ence"),
    ("correspond", "Double R"), ("criticise", "c-i-s-e"), ("curiosity", "os-ity"),
    ("definite", "fini in the middle"), ("desperate", "rat in the middle"), ("determined", "term in the middle"),
    ("develop", "No e at the end"), ("dictionary", "tion-ary"), ("disastrous", "No e in aster"),
    ("embarrass", "Double R, Double S"), ("environment", "ron-ment"), ("equipment", "equip-ment"),
    ("especially", "ci-ally"), ("exaggerate", "Double G"), ("excellent", "Double L"),
    ("existence", "ten-ce"), ("explanation", "pla-nation"), ("familiar", "liar at the end"),
    ("foreign", "re-ign"), ("forty", "No u"), ("frequently", "qu"),
    ("government", "vern-ment"), ("guarantee", "u-a-r"), ("harass", "One R, Double S"),
    ("hindrance", "drance"), ("identity", "tity"), ("immediate", "Double M")
]

READING_BANK = [
    {"text": "The volcano erupted, spewing hot lava down the mountain. What came out of the volcano?", "ans": "lava", "hint": "Hot liquid rock."},
    {"text": "Sherlock used his magnifying glass to find the tiny clue. What tool did he use?", "ans": "magnifying glass", "hint": "Used to make things look bigger."},
    {"text": "The Titanic hit an iceberg and began to sink. What did the ship hit?", "ans": "iceberg", "hint": "Large ice in sea."},
    {"text": "Photosynthesis is how plants use sunlight to make food. What do plants use to make food?", "ans": "sunlight", "hint": "Comes from the sun."},
    {"text": "The exhausted runner collapsed after crossing the finish line. How did the runner feel?", "ans": "exhausted", "hint": "Very tired."},
]

SHOP_ITEMS = [
    {"id": "s1", "name": "Recruit", "icon": "👦", "cost": 0},
    {"id": "s2", "name": "Soldier", "icon": "🪖", "cost": 100},
    {"id": "s3", "name": "Ninja", "icon": "🥷", "cost": 250},
    {"id": "s4", "name": "Robot", "icon": "🤖", "cost": 500},
    {"id": "s5", "name": "Wizard", "icon": "🧙‍♂️", "cost": 800},
    {"id": "s6", "name": "Cyborg", "icon": "🦾", "cost": 1200},
    {"id": "s7", "name": "King", "icon": "👑", "cost": 2000},
    {"id": "s8", "name": "Dragon", "icon": "🐲", "cost": 5000},
    {"id": "s9", "name": "God Mode", "icon": "⚡", "cost": 10000},
]

LEVEL_MAP = {
    1: {"name": "Training Field", "icon": "🪵", "hp": 30},
    2: {"name": "Slime Pit", "icon": "🐌", "hp": 50},
    3: {"name": "Wolf Den", "icon": "🐺", "hp": 70},
    4: {"name": "Goblin Camp", "icon": "👺", "hp": 90},
    5: {"name": "Skeleton Crypt", "icon": "💀", "hp": 120},
    6: {"name": "Orc Fortress", "icon": "🧟", "hp": 150},
    7: {"name": "Haunted Spire", "icon": "👻", "hp": 180},
    8: {"name": "Lava Core", "icon": "🔥", "hp": 220},
    9: {"name": "The Void", "icon": "🌑", "hp": 260},
    10: {"name": "THE SATS KING", "icon": "🏆", "hp": 350},
}

# ==========================================
# 💾 LOGIC & SYSTEM
# ==========================================

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"gold": 0, "level": 1, "tier": 1, "skins": ["s1"], "equipped": "s1"}
    try:
        df = pd.read_csv(DATA_FILE)
        skins_list = df['skins'].iloc[0].split("|")
        return {
            "gold": int(df['gold'].iloc[0]),
            "level": int(df['level'].iloc[0]),
            "tier": int(df.get('tier', [1]).iloc[0]), # Default to Tier 1 if missing
            "skins": skins_list,
            "equipped": str(df['equipped'].iloc[0])
        }
    except:
        return {"gold": 0, "level": 1, "tier": 1, "skins": ["s1"], "equipped": "s1"}

def save_data(data):
    skins_str = "|".join(data['skins'])
    df = pd.DataFrame({
        "gold": [data['gold']], 
        "level": [data['level']], 
        "tier": [data['tier']],
        "skins": [skins_str], 
        "equipped": [data['equipped']]
    })
    df.to_csv(DATA_FILE, index=False)

def get_next_question():
    """RNG Logic: 60% Maths (Infinite), 20% Spell, 20% Read"""
    roll = random.random()
    
    if roll < 0.6:
        # Generate Infinite Maths
        return MathEngine.generate()
    elif roll < 0.8:
        # Pick Random Spelling
        word, hint = random.choice(SPELLING_BANK)
        return {"type": "spell", "text": f"Spell the word for: '{hint}'", "ans": word, "hint": f"Starts with {word[0]}..."}
    else:
        # Pick Random Reading
        q = random.choice(READING_BANK)
        return {"type": "read", "text": q['text'], "ans": q['ans'], "hint": q['hint']}

# --- INIT ---
if 'profile' not in st.session_state:
    st.session_state['profile'] = load_data()

# Battle State
if 'battle' not in st.session_state:
    lvl = st.session_state['profile']['level']
    tier = st.session_state['profile']['tier']
    
    # Scale HP based on Tier (Prestige Level)
    base_hp = LEVEL_MAP.get(lvl, LEVEL_MAP[10])['hp']
    scaled_hp = int(base_hp * (1 + (tier - 1) * 0.5))
    
    st.session_state['battle'] = {
        "hp": scaled_hp,
        "max_hp": scaled_hp,
        "q": get_next_question(),
        "misses": 0,
        "log": f"Entering Tier {tier} Combat..."
    }

# ==========================================
# 🖥️ UI RENDER
# ==========================================

# HEADER
c1, c2, c3 = st.columns([2, 1, 1])
with c1:
    st.markdown(f"### 🛡️ Sonny's RPG <span class='prestige-badge'>Tier {st.session_state['profile']['tier']}</span>", unsafe_allow_html=True)
with c2:
    st.markdown(f"💰 **{st.session_state['profile']['gold']}**")
with c3:
    lvl_name = LEVEL_MAP.get(st.session_state['profile']['level'], {}).get('name', 'Unknown')
    st.caption(f"Level {st.session_state['profile']['level']}: {lvl_name}")

tab_battle, tab_shop = st.tabs(["⚔️ BATTLE", "🛒 SHOP"])

with tab_battle:
    profile = st.session_state['profile']
    battle = st.session_state['battle']
    lvl_info = LEVEL_MAP.get(profile['level'], LEVEL_MAP[10])
    
    # 1. BATTLEFIELD
    c_ply, c_mid, c_mon = st.columns([1, 0.2, 1])
    
    with c_ply:
        icon = next((s['icon'] for s in SHOP_ITEMS if s['id'] == profile['equipped']), "👦")
        st.markdown(f"<div style='font-size: 80px; text-align: center;'>{icon}</div>", unsafe_allow_html=True)
    
    with c_mon:
        st.markdown(f"""
        <div class='monster-card'>
            <div style='font-size: 60px;'>{lvl_info['icon']}</div>
            <h5>{lvl_info['name']} (Tier {profile['tier']})</h5>
        </div>
        """, unsafe_allow_html=True)
        
        # HP Bar
        hp_pct = max(0.0, battle['hp'] / battle['max_hp'])
        st.progress(hp_pct, text=f"HP: {max(0, battle['hp'])}/{battle['max_hp']}")

    # 2. LOGS
    st.divider()
    if battle['misses'] > 0: st.warning(f"💡 HINT: {battle['q']['hint']}")
    if "CRITICAL" in battle['log']: st.success(battle['log'])
    elif "BLOCKED" in battle['log']: st.info(battle['log'])

    # 3. COMBAT INPUT
    if battle['hp'] > 0:
        st.markdown(f"**QUESTION:** {battle['q']['text']}")
        
        with st.form("combat", clear_on_submit=True):
            col_in, col_btn = st.columns([3, 1])
            with col_in:
                ans = st.text_input("Answer", label_visibility="collapsed")
            with col_btn:
                attack = st.form_submit_button("⚔️")
            
            if attack:
                target = str(battle['q']['ans']).lower().strip()
                guess = str(ans).lower().strip()
                
                # Check Logic (Partial match for reading, exact for math)
                correct = False
                if battle['q']['type'] == 'read':
                    if guess in target and len(guess) > 2: correct = True
                elif guess == target:
                    correct = True
                    
                if correct:
                    dmg = 35 + (profile['tier'] * 5) # Damage scales with prestige
                    battle['hp'] -= dmg
                    profile['gold'] += 15 * profile['tier'] # Gold scales with prestige
                    battle['log'] = f"HIT! +{15 * profile['tier']} Gold"
                    
                    if battle['hp'] > 0:
                        battle['q'] = get_next_question()
                        battle['misses'] = 0
                    
                    save_data(profile)
                    st.rerun()
                else:
                    battle['misses'] += 1
                    battle['log'] = "BLOCKED!"
                    st.rerun()
    else:
        # VICTORY / LEVEL UP
        st.balloons()
        
        if profile['level'] == 10:
            # PRESTIGE MOMENT
            st.markdown(f"<h2 style='text-align: center; color: #DD2476;'>👑 TIER {profile['tier']} COMPLETED! 👑</h2>", unsafe_allow_html=True)
            st.info("The monsters grow stronger... but the rewards are greater.")
            if st.button("🔥 ENTER NEXT TIER (PRESTIGE)", type="primary", use_container_width=True):
                profile['level'] = 1
                profile['tier'] += 1
                # Setup Level 1 (Tier X)
                base_hp = LEVEL_MAP[1]['hp']
                scaled_hp = int(base_hp * (1 + (profile['tier'] - 1) * 0.5))
                battle['hp'] = scaled_hp
                battle['max_hp'] = scaled_hp
                battle['q'] = get_next_question()
                battle['log'] = f"Welcome to Tier {profile['tier']}..."
                save_data(profile)
                st.rerun()
        else:
            # NORMAL LEVEL UP
            if st.button("➡️ NEXT LEVEL", type="primary", use_container_width=True):
                profile['level'] += 1
                # Setup Next Level
                base_hp = LEVEL_MAP[profile['level']]['hp']
                scaled_hp = int(base_hp * (1 + (profile['tier'] - 1) * 0.5))
                battle['hp'] = scaled_hp
                battle['max_hp'] = scaled_hp
                battle['q'] = get_next_question()
                battle['log'] = f"Entering {LEVEL_MAP[profile['level']]['name']}..."
                save_data(profile)
                st.rerun()

with tab_shop:
    st.caption("Prestige to earn gold faster and unlock the Dragon!")
    cols = st.columns(3)
    for i, item in enumerate(SHOP_ITEMS):
        with cols[i % 3]:
            owned = item['id'] in profile['skins']
            equipped = item['id'] == profile['equipped']
            
            border = "2px solid #FFD700" if equipped else "1px solid #555"
            st.markdown(f"<div style='border: {border}; background: #222; padding: 10px; border-radius: 10px; text-align: center; margin-bottom: 10px;'><div style='font-size: 40px;'>{item['icon']}</div><b>{item['name']}</b><br><span style='color: #FFD700'>{item['cost']}g</span></div>", unsafe_allow_html=True)
            
            if equipped: st.button("EQUIPPED", key=f"s_{item['id']}", disabled=True)
            elif owned:
                if st.button("EQUIP", key=f"s_{item['id']}"):
                    profile['equipped'] = item['id']
                    save_data(profile)
                    st.rerun()
            else:
                if st.button("BUY", key=f"s_{item['id']}"):
                    if profile['gold'] >= item['cost']:
                        profile['gold'] -= item['cost']
                        profile['skins'].append(item['id'])
                        save_data(profile)
                        st.rerun()
                    else: st.toast("Need more gold!")

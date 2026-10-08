"""
feedback_analyzer.py - Customer feedback analysis, sentiment scoring, NPS calculation, and pain-point extraction.
"""

import re
import numpy as np
import pandas as pd
from typing import Dict, Any, List


POSITIVE_LEXICON = {
    "love", "exceeded", "great", "best", "seamless", "effortless", "quiet",
    "saved", "cheaper", "reliable", "impressed", "game-changer", "fast", "smooth",
    "valuable", "plenty", "happy", "excellent", "instant", "satisfaction"
}

NEGATIVE_LEXICON = {
    "anxiety", "broken", "stressful", "penalty", "severe", "queue", "failures",
    "lacking", "premium", "higher", "expensive", "lag", "distracting", "degradation",
    "failure", "shop", "wear", "slow", "poor", "issue", "worst", "frustrating"
}


def analyze_sentiment_rule(text: str) -> str:
    """
    Lightweight rule-based sentiment classifier for customer review text.
    """
    words = re.findall(r'\b[a-z\-]+\b', text.lower())
    pos_score = sum(1 for w in words if w in POSITIVE_LEXICON)
    neg_score = sum(1 for w in words if w in NEGATIVE_LEXICON)

    if pos_score > neg_score:
        return "Positive"
    elif neg_score > pos_score:
        return "Negative"
    return "Neutral"


def analyze_customer_feedback(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Computes overall satisfaction, NPS, category ratings, sentiment distribution, and key issues.
    """
    if df.empty:
        return {}

    # Ensure rating is numeric
    df = df.copy()
    df["Rating"] = pd.to_numeric(df["Rating"], errors="coerce").fillna(3).astype(int)

    # Re-evaluate or harmonize Sentiment if missing
    if "Sentiment" not in df.columns:
        df["Sentiment"] = df["Feedback_Text"].apply(analyze_sentiment_rule)

    total_reviews = len(df)
    avg_rating = round(float(df["Rating"].mean()), 2)
    satisfied_pct = round(float((df["Rating"] >= 4).sum() / total_reviews * 100), 1)

    # NPS Calculation: Promoters (5) - Detractors (1, 2, 3)
    promoters_count = (df["Rating"] == 5).sum()
    passives_count = (df["Rating"] == 4).sum()
    detractors_count = (df["Rating"] <= 3).sum()

    nps = round(((promoters_count - detractors_count) / total_reviews) * 100, 1)

    # Sentiment Breakdown
    sentiment_counts = df["Sentiment"].value_counts().to_dict()
    sentiment_dist = {
        "Positive": sentiment_counts.get("Positive", 0),
        "Neutral": sentiment_counts.get("Neutral", 0),
        "Negative": sentiment_counts.get("Negative", 0)
    }

    # Category Breakdown
    category_summary = []
    for cat, cat_group in df.groupby("Category"):
        cat_total = len(cat_group)
        cat_avg = round(float(cat_group["Rating"].mean()), 2)
        cat_pos = round(float((cat_group["Sentiment"] == "Positive").sum() / cat_total * 100), 1)
        cat_neg = round(float((cat_group["Sentiment"] == "Negative").sum() / cat_total * 100), 1)
        cat_neu = round(100.0 - cat_pos - cat_neg, 1)

        category_summary.append({
            "Category": cat,
            "Total_Reviews": cat_total,
            "Avg_Rating": cat_avg,
            "Positive_Pct": cat_pos,
            "Negative_Pct": cat_neg,
            "Neutral_Pct": cat_neu
        })

    cat_df = pd.DataFrame(category_summary).sort_values(by="Avg_Rating", ascending=True)

    # Top keywords / recurring themes in negative reviews
    neg_reviews = df[df["Sentiment"] == "Negative"]["Feedback_Text"].str.cat(sep=" ")
    neg_words = re.findall(r'\b[a-z]{4,}\b', neg_reviews.lower())
    stop_words = {"this", "that", "with", "from", "have", "after", "than", "make", "when", "into", "their"}
    freq = {}
    for w in neg_words:
        if w not in stop_words and w in NEGATIVE_LEXICON:
            freq[w] = freq.get(w, 0) + 1
    top_pain_keywords = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:8]

    # Automated strategic recommendations
    recommendations = generate_strategic_recommendations(cat_df)

    return {
        "total_reviews": total_reviews,
        "avg_rating": avg_rating,
        "satisfied_pct": satisfied_pct,
        "nps": nps,
        "promoters": promoters_count,
        "passives": passives_count,
        "detractors": detractors_count,
        "sentiment_distribution": sentiment_dist,
        "category_summary": cat_df,
        "top_pain_keywords": top_pain_keywords,
        "recommendations": recommendations,
        "raw_reviews": df
    }


def generate_strategic_recommendations(cat_df: pd.DataFrame) -> List[Dict[str, str]]:
    """
    Generates tailored strategic recommendations based on low-scoring feedback categories.
    """
    recs = []
    for _, row in cat_df.iterrows():
        cat = row["Category"]
        avg = row["Avg_Rating"]
        neg = row["Negative_Pct"]

        if "Charging" in cat and (avg < 3.8 or neg > 25):
            recs.append({
                "area": "Charging Infrastructure Reliability",
                "severity": "High",
                "finding": f"High customer friction ({neg}% negative) regarding charger uptime and payment reader reliability.",
                "action": "Implement uptime service level agreements (SLAs >97%), mandate automated ISO 15118 Plug & Charge, and add real-time stall availability telemetry."
            })
        elif "Range" in cat and (avg < 3.8 or neg > 25):
            recs.append({
                "area": "Winter & Highway Range Anxiety",
                "severity": "Medium",
                "finding": f"Drivers report significant cold weather range drop and highway efficiency decay ({neg}% negative).",
                "action": "Incorporate intelligent battery preconditioning into standard navigation routing and expand high-speed fast chargers along rural highway corridors."
            })
        elif "Price" in cat and (avg < 3.8 or neg > 25):
            recs.append({
                "area": "Upfront Purchase & Maintenance Costs",
                "severity": "Medium",
                "finding": f"Customers cite high initial acquisition price and elevated EV tire wear costs.",
                "action": "Expand point-of-sale clean vehicle rebates, encourage EV-specific tire formulations with lower rolling resistance, and promote off-peak utility charging tariffs."
            })
        elif "Battery" in cat and (avg < 3.8 or neg > 25):
            recs.append({
                "area": "Battery Health & Warranty Transparency",
                "severity": "Medium",
                "finding": f"Owner concerns over long-term battery degradation and inverter parts availability.",
                "action": "Provide standardized in-dashboard battery health state-of-health (SoH) diagnostics and extend certified pre-owned battery warranties."
            })
        elif "Performance" in cat and (avg < 3.8 or neg > 25):
            recs.append({
                "area": "Infotainment & Physical Controls",
                "severity": "Low",
                "finding": f"Complaints regarding touchscreen menu lag and lack of tactile HVAC buttons.",
                "action": "Optimize infotainment software response latency via over-the-air (OTA) updates and retain dedicated hardware controls for safety-critical functions."
            })

    if not recs:
        recs.append({
            "area": "Overall Adoption Momentum",
            "severity": "Low",
            "finding": "Customer satisfaction remains generally strong across all surveyed categories.",
            "action": "Maintain current expansion trajectory while monitoring charger utilization rates as fleet scale doubles."
        })

    return recs


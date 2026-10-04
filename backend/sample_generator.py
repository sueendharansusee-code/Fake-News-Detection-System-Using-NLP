import os
import pandas as pd

SAMPLE_ARTICLES = [
    # REAL NEWS SAMPLES (Label: 1 or 'REAL')
    {
        "text": "NASA launches James Webb Space Telescope to observe early universe galaxies and study distant exoplanets in unprecedented detail.",
        "label": "REAL"
    },
    {
        "text": "The Federal Reserve announced an adjustment to interest rates following the latest consumer price index report showing moderation in inflation data.",
        "label": "REAL"
    },
    {
        "text": "Researchers at Oxford University report promising results in phase 3 clinical trials for a novel malaria vaccine showing high efficacy in children.",
        "label": "REAL"
    },
    {
        "text": "Global renewable energy capacity grew by a record percentage last year led by massive expansions in solar power and wind generation infrastructure.",
        "label": "REAL"
    },
    {
        "text": "The European Union passes landmark artificial intelligence regulations setting comprehensive compliance standards for high-risk machine learning models.",
        "label": "REAL"
    },
    {
        "text": "Electric vehicle sales reached new record highs across North America and Europe driven by battery efficiency improvements and infrastructure investment.",
        "label": "REAL"
    },
    {
        "text": "Archaeologists discover ancient Roman settlement ruins beneath city center during metro expansion project in central Italy.",
        "label": "REAL"
    },
    {
        "text": "World Health Organization issues updated global health guidelines recommending reduced sodium intake and increased access to primary care.",
        "label": "REAL"
    },
    {
        "text": "Scientists discover new deep ocean hydrothermal vent ecosystem hosting previously unknown species of crustaceans and marine organisms.",
        "label": "REAL"
    },
    {
        "text": "Central bank leaders gather for annual summit to discuss monetary policy, economic stabilization, and international trade relations.",
        "label": "REAL"
    },
    {
        "text": "Tech company unveils quantum computing processor achieving improved qubit stability and error mitigation performance in benchmark tests.",
        "label": "REAL"
    },
    {
        "text": "Public health officials confirm decline in seasonal influenza transmission following widespread vaccination campaigns across regional health districts.",
        "label": "REAL"
    },
    {
        "text": "Astronomers detect repeating radio signals from a distant spiral galaxy using giant radio telescope array.",
        "label": "REAL"
    },
    {
        "text": "Department of Transportation approves major grant program to modernize aging bridges and interstate highway infrastructure across multiple states.",
        "label": "REAL"
    },
    {
        "text": "International climate agreement signatories convene to pledge accelerated reductions in industrial carbon emissions by end of decade.",
        "label": "REAL"
    },
    {
        "text": "Medical researchers publish peer-reviewed study demonstrating effectiveness of mRNA therapeutic platform for targeted cancer immunotherapy.",
        "label": "REAL"
    },
    {
        "text": "Agriculture department reports strong grain yields supported by favorable spring rainfall and advanced soil conservation practices.",
        "label": "REAL"
    },
    {
        "text": "City council votes to approve public transit expansion line connecting suburban residential areas with downtown financial district.",
        "label": "REAL"
    },
    {
        "text": "Cybersecurity coalition issues advisories detailing patch updates for critical software vulnerabilities affecting enterprise servers.",
        "label": "REAL"
    },
    {
        "text": "Global supply chains show signs of normalization as freight container shipping costs return to pre-pandemic baseline averages.",
        "label": "REAL"
    },
    {
        "text": "Marine biologists track migration patterns of humpback whales using satellite tagging technology in the North Pacific Ocean.",
        "label": "REAL"
    },
    {
        "text": "National Weather Service issues winter storm advisories for Midwestern states forecasting heavy snowfall and freezing temperatures.",
        "label": "REAL"
    },
    {
        "text": "University physics lab achieves plasma confinement breakthrough in nuclear fusion reactor test run.",
        "label": "REAL"
    },
    {
        "text": "Stock market index closes higher following positive quarterly earnings reports from leading technology and manufacturing firms.",
        "label": "REAL"
    },
    {
        "text": "Conservation group announces successful restoration of coastal wetland habitat supporting endangered migratory bird species.",
        "label": "REAL"
    },
    {
        "text": "Biotech startup receives regulatory approval to begin clinical trials for synthetic antibody therapy targeting autoimmune disorders.",
        "label": "REAL"
    },
    {
        "text": "High court renders unanimous decision upholding environmental protection standards for freshwater river basins.",
        "label": "REAL"
    },
    {
        "text": "Robotics engineers demonstrate autonomous drone fleet capable of assisting emergency responders during natural disaster rescue missions.",
        "label": "REAL"
    },
    {
        "text": "Telecom consortium begins deployment of next generation high-speed fiber optic internet infrastructure across rural communities.",
        "label": "REAL"
    },
    {
        "text": "Pharmaceutical regulatory board approves new oral antiviral treatment for respiratory virus management.",
        "label": "REAL"
    },

    # FAKE NEWS SAMPLES (Label: 0 or 'FAKE')
    {
        "text": "SHOCKING SECRET: Whistleblower reveals secret alien base inside Earth's core controlled by underground Illuminati elites!",
        "label": "FAKE"
    },
    {
        "text": "MIRACLE CURE: Doctors are stunned! Drinking boiled lemon water with baking soda cures all known diseases overnight! Big Pharma tried to ban this video!",
        "label": "FAKE"
    },
    {
        "text": "BANNED TRUTH: Governments secretly controlling global weather with mind control towers! Share before censorship deletes this link!",
        "label": "FAKE"
    },
    {
        "text": "BREAKING: Scientists confirm 5G cell phone towers are transmitting mind-reading signals to control consumer spending habits!",
        "label": "FAKE"
    },
    {
        "text": "EXCLUSIVE: Ancient 10,000 year old giant skeleton discovered in backyard proves humans were created by extra-terrestrial visitors!",
        "label": "FAKE"
    },
    {
        "text": "SECRET DOCUMENTS LEAKED: Drinking tap water turns your teeth into microchip antennas according to top anonymous doctor!",
        "label": "FAKE"
    },
    {
        "text": "YOU WON'T BELIEVE THIS! Billionaire secretly buys moon to construct private luxury resort for elite politicians only!",
        "label": "FAKE"
    },
    {
        "text": "PROOF: Time traveler from year 3000 warns that eating broccoli causes instant memory loss! Mainstream media hiding the evidence!",
        "label": "FAKE"
    },
    {
        "text": "SHOCKING DISCOVERY: Eating banana peels every morning grants immortal youth and cures aging! Dermatologists hate this one simple trick!",
        "label": "FAKE"
    },
    {
        "text": "URGENT WARNING: NASA admits Earth will lose gravity for 3 hours next Tuesday! Experts urge citizens to tie themselves to heavy furniture!",
        "label": "FAKE"
    },
    {
        "text": "HIDDEN CONSPIRACY: Secret society replacing city pigeons with spy cameras equipped with facial recognition laser eyes!",
        "label": "FAKE"
    },
    {
        "text": "HOLY GRAIL FOUND: Anonymous researcher discovers magic frequency sound that melts belly fat while you sleep with zero effort!",
        "label": "FAKE"
    },
    {
        "text": "CONFIRMED: Government agency planning to replace paper money with digital bio-chips injected under your fingernails!",
        "label": "FAKE"
    },
    {
        "text": "SCANDAL: World leaders secretly meeting inside hollowed-out volcano to control global egg prices!",
        "label": "FAKE"
    },
    {
        "text": "UNBELIEVABLE: Putting garlic in your socks cures diabetes in 24 hours! Health industry desperately suppressing this ancient secret!",
        "label": "FAKE"
    },
    {
        "text": "ALERT: Atmospheric cloud seeding chemical spray detected in household air conditioners! Turn off your AC units immediately!",
        "label": "FAKE"
    },
    {
        "text": "BOMBSHELL REVELATION: Ancient pyramids were actually massive wireless cell phone chargers built by Atlantis superhumans!",
        "label": "FAKE"
    },
    {
        "text": "WARNING: Commercial airlines spraying memory-wiping gas over major cities during routine flights! See photos here!",
        "label": "FAKE"
    },
    {
        "text": "DOCTORS FURIOUS: Local grandmother discovers one weird plant that erases arthritis pain forever! Medical industry panicking!",
        "label": "FAKE"
    },
    {
        "text": "SHOCKING EVIDENCE: Moon landing was staged inside a underwater swimming pool in Hollywood backlot!",
        "label": "FAKE"
    },
    {
        "text": "REVEALED: Secret subterranean tunnel network connects London directly to New York City built by ancient occultists!",
        "label": "FAKE"
    },
    {
        "text": "EXPOSED: Synthetic artificial rain containing micro-robots engineered to make citizens obey radio broadcasts!",
        "label": "FAKE"
    },
    {
        "text": "AMAZING SECRET: Sleeping under aluminum foil blanket boosts IQ by 50 points in 3 days! Teachers don't want you to know!",
        "label": "FAKE"
    },
    {
        "text": "BREAKING NEWS: Giant sea monster spotted swallowed entire cargo ship in Bermuda Triangle! Navy covers up incident!",
        "label": "FAKE"
    },
    {
        "text": "SCIENTISTS TERRORIZED: New super-food berry makes people speak 10 languages overnight without studying!",
        "label": "FAKE"
    },
    {
        "text": "CHILLING REPORT: Smart TVs secretly recording family conversations and selling dreams to advertising corporations!",
        "label": "FAKE"
    },
    {
        "text": "WHISTLEBLOWER ACCIDENTALLY LEAKS FILE: Sunlight is actually artificial light emitted from giant orbital mirror satellite!",
        "label": "FAKE"
    },
    {
        "text": "DON'T LOOK NOW: Staring directly at microwave ovens while cooking endows temporary telepathic abilities claims viral video!",
        "label": "FAKE"
    },
    {
        "text": "BANNED HEALTH HACK: Rubbing coconut oil on your phone screen doubles battery life and prevents internet radiation!",
        "label": "FAKE"
    },
    {
        "text": "SHOCKING TRUTH: World's oceans are actually filling up with liquid jello according to rogue marine biologist!",
        "label": "FAKE"
    }
]

def generate_sample_dataset(output_path=None):
    """
    Generates a sample CSV dataset if it does not exist.
    Returns pandas DataFrame.
    """
    if output_path is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(base_dir, "data")
        output_path = os.path.join(data_dir, "sample_news.csv")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    df = pd.DataFrame(SAMPLE_ARTICLES)
    df.to_csv(output_path, index=False, encoding="utf-8")
    print(f"[Sample Generator] Created sample dataset at: {output_path} ({len(df)} rows)")
    return df

if __name__ == "__main__":
    generate_sample_dataset()

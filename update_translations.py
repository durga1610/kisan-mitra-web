import re

# New translations to add
new_keys = [
    "Search Settings...", "Search Results", "Account Settings", "App Preferences",
    "Data & Sync", "Security", "Support & Legal", "Edit Profile", "Change Password",
    "Dark Mode", "Push Notifications", "Weather Alerts", "Market Price Alerts",
    "Auto Backup Data", "App Permissions", "Report a Problem", "Feedback", "Rate App",
    "Terms & Conditions", "FAQ",
    "How do I add a new crop?", "Go to the Home tab and click 'Add Crop' at the top right.",
    "Why are market prices not updating?", "Please ensure you have an active internet connection. Prices sync daily.",
    "How accurate is the AI recommendation?", "Our AI uses live market data and weather APIs for high accuracy.",
    "Attach Screenshot", "Cancel", "Submit", "Send Feedback", "Update Password",
    "Enable Alerts", "Done", "Backup & Sync", "Auto Backup", "Sync data daily over Wi-Fi",
    "Backup Now", "Camera", "Location", "Open OS Settings", "Contact Support", "Call Us",
    "Email Support", "WhatsApp", "Live Chat (AI)",
    "Are you sure you want to log out of your account?", "Yes, Logout",
    "This action cannot be undone. All your farm data, history, and preferences will be permanently removed.",
    "Delete Permanently", "Title", "Description",
    "By using Kisan Mitra, you agree to the following terms...\\n\\n1. Use responsibly...\\n2. No illegal activities."
]

translations = {
    'hi': {
        "Search Settings...": "सेटिंग्स खोजें...",
        "Search Results": "खोज परिणाम",
        "Account Settings": "खाता सेटिंग्स",
        "App Preferences": "ऐप प्राथमिकताएं",
        "Data & Sync": "डेटा और सिंक",
        "Security": "सुरक्षा",
        "Support & Legal": "समर्थन और कानूनी",
        "Edit Profile": "प्रोफ़ाइल संपादित करें",
        "Change Password": "पासवर्ड बदलें",
        "Dark Mode": "डार्क मोड",
        "Push Notifications": "पुश सूचनाएं",
        "Weather Alerts": "मौसम अलर्ट",
        "Market Price Alerts": "मंडी भाव अलर्ट",
        "Auto Backup Data": "ऑटो बैकअप डेटा",
        "App Permissions": "ऐप अनुमतियां",
        "Report a Problem": "समस्या की रिपोर्ट करें",
        "Feedback": "प्रतिक्रिया",
        "Rate App": "ऐप को रेट करें",
        "Terms & Conditions": "नियम और शर्तें",
        "FAQ": "अक्सर पूछे जाने वाले प्रश्न",
        "How do I add a new crop?": "मैं एक नई फसल कैसे जोड़ूं?",
        "Go to the Home tab and click 'Add Crop' at the top right.": "होम टैब पर जाएं और ऊपर दाईं ओर 'फसल जोड़ें' पर क्लिक करें।",
        "Why are market prices not updating?": "बाजार भाव अपडेट क्यों नहीं हो रहे हैं?",
        "Please ensure you have an active internet connection. Prices sync daily.": "कृपया सुनिश्चित करें कि आपके पास एक सक्रिय इंटरनेट कनेक्शन है। कीमतें प्रतिदिन सिंक होती हैं।",
        "How accurate is the AI recommendation?": "AI की सिफारिश कितनी सटीक है?",
        "Our AI uses live market data and weather APIs for high accuracy.": "हमारा AI उच्च सटीकता के लिए लाइव मार्केट डेटा और मौसम API का उपयोग करता है।",
        "Attach Screenshot": "स्क्रीनशॉट संलग्न करें",
        "Cancel": "रद्द करें",
        "Submit": "जमा करें",
        "Send Feedback": "प्रतिक्रिया भेजें",
        "Update Password": "पासवर्ड अपडेट करें",
        "Enable Alerts": "अलर्ट सक्षम करें",
        "Done": "हो गया",
        "Backup & Sync": "बैकअप और सिंक",
        "Auto Backup": "ऑटो बैकअप",
        "Sync data daily over Wi-Fi": "वाई-फाई पर प्रतिदिन डेटा सिंक करें",
        "Backup Now": "अभी बैकअप लें",
        "Camera": "कैमरा",
        "Location": "स्थान",
        "Open OS Settings": "OS सेटिंग्स खोलें",
        "Contact Support": "समर्थन से संपर्क करें",
        "Call Us": "हमें कॉल करें",
        "Email Support": "ईमेल समर्थन",
        "WhatsApp": "व्हाट्सएप",
        "Live Chat (AI)": "लाइव चैट (AI)",
        "Are you sure you want to log out of your account?": "क्या आप वाकई अपने खाते से लॉग आउट करना चाहते हैं?",
        "Yes, Logout": "हां, लॉग आउट करें",
        "This action cannot be undone. All your farm data, history, and preferences will be permanently removed.": "इस क्रिया को पूर्ववत नहीं किया जा सकता है। आपका सभी खेत का डेटा, इतिहास और प्राथमिकताएं स्थायी रूप से हटा दी जाएंगी।",
        "Delete Permanently": "स्थायी रूप से हटाएं",
        "Title": "शीर्षक",
        "Description": "विवरण",
        "By using Kisan Mitra, you agree to the following terms...\\n\\n1. Use responsibly...\\n2. No illegal activities.": "किसान मित्र का उपयोग करके, आप निम्नलिखित शर्तों से सहमत होते हैं...\\n\\n1. जिम्मेदारी से उपयोग करें...\\n2. कोई अवैध गतिविधियां नहीं।"
    },
    'te': {
        "Search Settings...": "సెట్టింగ్‌లను వెతకండి...",
        "Search Results": "శోధన ఫలితాలు",
        "Account Settings": "ఖాతా సెట్టింగ్‌లు",
        "App Preferences": "యాప్ ప్రాధాన్యతలు",
        "Data & Sync": "డేటా & సింక్",
        "Security": "భద్రత",
        "Support & Legal": "మద్దతు & చట్టబద్ధమైనవి",
        "Edit Profile": "ప్రొఫైల్‌ను సవరించండి",
        "Change Password": "పాస్‌వర్డ్ మార్చండి",
        "Dark Mode": "డార్క్ మోడ్",
        "Push Notifications": "పుష్ నోటిఫికేషన్‌లు",
        "Weather Alerts": "వాతావరణ హెచ్చరికలు",
        "Market Price Alerts": "మార్కెట్ ధర హెచ్చరికలు",
        "Auto Backup Data": "ఆటో బ్యాకప్ డేటా",
        "App Permissions": "యాప్ అనుమతులు",
        "Report a Problem": "సమస్యను నివేదించండి",
        "Feedback": "అభిప్రాయం",
        "Rate App": "యాప్‌ను రేట్ చేయండి",
        "Terms & Conditions": "నియమాలు & షరతులు",
        "FAQ": "తరచుగా అడిగే ప్రశ్నలు",
        "How do I add a new crop?": "కొత్త పంటను ఎలా జోడించాలి?",
        "Go to the Home tab and click 'Add Crop' at the top right.": "హోమ్ ట్యాబ్‌కు వెళ్లి పైన కుడి వైపున ఉన్న 'పంటను జోడించు' క్లిక్ చేయండి.",
        "Why are market prices not updating?": "మార్కెట్ ధరలు ఎందుకు అప్‌డేట్ అవ్వడం లేదు?",
        "Please ensure you have an active internet connection. Prices sync daily.": "దయచేసి మీకు యాక్టివ్ ఇంటర్నెట్ కనెక్షన్ ఉందని నిర్ధారించుకోండి. ధరలు ప్రతిరోజూ సింక్ అవుతాయి.",
        "How accurate is the AI recommendation?": "AI సిఫార్సు ఎంత ఖచ్చితమైనది?",
        "Our AI uses live market data and weather APIs for high accuracy.": "అధిక ఖచ్చితత్వం కోసం మా AI లైవ్ మార్కెట్ డేటా మరియు వాతావరణ APIలను ఉపయోగిస్తుంది.",
        "Attach Screenshot": "స్క్రీన్‌షాట్‌ను జోడించండి",
        "Cancel": "రద్దు చేయండి",
        "Submit": "సమర్పించండి",
        "Send Feedback": "అభిప్రాయాన్ని పంపండి",
        "Update Password": "పాస్‌వర్డ్ అప్‌డేట్ చేయండి",
        "Enable Alerts": "హెచ్చరికలను ప్రారంభించండి",
        "Done": "పూర్తయింది",
        "Backup & Sync": "బ్యాకప్ & సింక్",
        "Auto Backup": "ఆటో బ్యాకప్",
        "Sync data daily over Wi-Fi": "Wi-Fi ద్వారా ప్రతిరోజూ డేటాను సింక్ చేయండి",
        "Backup Now": "ఇప్పుడే బ్యాకప్ చేయండి",
        "Camera": "కెమెరా",
        "Location": "స్థానం",
        "Open OS Settings": "OS సెట్టింగ్‌లను తెరవండి",
        "Contact Support": "మద్దతును సంప్రదించండి",
        "Call Us": "మాకు కాల్ చేయండి",
        "Email Support": "ఈమెయిల్ మద్దతు",
        "WhatsApp": "వాట్సాప్",
        "Live Chat (AI)": "లైవ్ చాట్ (AI)",
        "Are you sure you want to log out of your account?": "మీరు ఖచ్చితంగా మీ ఖాతా నుండి లాగ్ అవుట్ చేయాలనుకుంటున్నారా?",
        "Yes, Logout": "అవును, లాగ్ అవుట్ చేయండి",
        "This action cannot be undone. All your farm data, history, and preferences will be permanently removed.": "ఈ చర్యను వెనక్కి తీసుకోలేము. మీ మొత్తం వ్యవసాయ డేటా, చరిత్ర మరియు ప్రాధాన్యతలు శాశ్వతంగా తీసివేయబడతాయి.",
        "Delete Permanently": "శాశ్వతంగా తొలగించండి",
        "Title": "శీర్షిక",
        "Description": "వివరణ",
        "By using Kisan Mitra, you agree to the following terms...\\n\\n1. Use responsibly...\\n2. No illegal activities.": "కిసాన్ మిత్రను ఉపయోగించడం ద్వారా, మీరు ఈ క్రింది నిబంధనలకు అంగీకరిస్తున్నారు...\\n\\n1. బాధ్యతాయుతంగా ఉపయోగించండి...\\n2. అక్రమ కార్యకలాపాలు చేయవద్దు."
    }
}

filepath = 'lib/core/localization/app_translations.dart'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# For 'en', we just add the key: key
# For 'hi' and 'te', we add the translation, or fallback to english.
# For others, fallback to english.

languages = ['en', 'hi', 'te', 'mr', 'ta', 'bn', 'gu', 'as', 'kn', 'ml', 'or', 'pa', 'ur', 'ks', 'kok', 'ne', 'sa']

for lang in languages:
    # Find where the lang dictionary ends
    # The dictionary looks like: 'lang': { \n ... \n    },
    pattern = re.compile(rf"('{lang}':\s*{{)(.*?)(\n\s*}},)", re.DOTALL)
    match = pattern.search(content)
    if match:
        existing_dict_content = match.group(2)
        new_dict_content = existing_dict_content
        
        for key in new_keys:
            # Check if key already exists
            if f"'{key}'" not in existing_dict_content and f'"{key}"' not in existing_dict_content:
                # get translation
                if lang == 'en':
                    val = key
                elif lang in translations and key in translations[lang]:
                    val = translations[lang][key]
                else:
                    val = key
                
                # properly escape quotes
                # If the key has single quotes, we should enclose in double quotes or escape
                key_escaped = key.replace("'", "\\'")
                val_escaped = val.replace("'", "\\'")
                
                new_dict_content += f"\n      '{key_escaped}': '{val_escaped}',"
                
        content = content[:match.start()] + match.group(1) + new_dict_content + match.group(3) + content[match.end():]

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated app_translations.dart successfully!")

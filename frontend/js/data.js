/**
 * AgriSense-AI: Agricultural Domain Data & Realistic Presets for Tamil Nadu Paddy Cultivation
 * Based on Tamil Nadu Agricultural University (TNAU) Agritech Portal standards.
 */

const AGRI_DATA = {
  // Major paddy-growing districts in Tamil Nadu with agro-climatic coordinates and typical baselines
  districts: {
    "Thanjavur": {
      name_ta: "தஞ்சாவூர்",
      zone: "Cauvery Delta Zone",
      zone_ta: "காவிரி டெல்டா மண்டலம்",
      typicalSoil: "Alluvial",
      avgRainfall: 1100,
      currentWeather: {
        temp: 31.5,
        humidity: 78,
        rainfall: 4.2,
        condition: "Partly Cloudy",
        condition_ta: "பகுதி மேகமூட்டம்",
        windSpeed: 14,
        uvIndex: 7,
        dewPoint: 24.2
      },
      forecast: [
        { day: "Mon", day_ta: "திங்கள்", high: 33, low: 25, condition: "Partly Cloudy", condition_ta: "மேகமூட்டம்", rainProb: 20 },
        { day: "Tue", day_ta: "செவ்வாய்", high: 32, low: 24, condition: "Scattered Rain", condition_ta: "சிதறிய மழை", rainProb: 65 },
        { day: "Wed", day_ta: "புதன்", high: 30, low: 23, condition: "Moderate Showers", condition_ta: "மிதமான மழை", rainProb: 80 },
        { day: "Thu", day_ta: "வியாழன்", high: 31, low: 24, condition: "Clear Sky", condition_ta: "தெளிவான வானம்", rainProb: 15 },
        { day: "Fri", day_ta: "வெள்ளி", high: 33, low: 25, condition: "Sunny", condition_ta: "வெயில்", rainProb: 10 }
      ]
    },
    "Tiruvarur": {
      name_ta: "திருவாரூர்",
      zone: "Cauvery Delta Zone",
      zone_ta: "காவிரி டெல்டா மண்டலம்",
      typicalSoil: "Clayey",
      avgRainfall: 1250,
      currentWeather: {
        temp: 30.8,
        humidity: 82,
        rainfall: 6.5,
        condition: "Light Rain",
        condition_ta: "லேசான மழை",
        windSpeed: 16,
        uvIndex: 6,
        dewPoint: 25.1
      },
      forecast: [
        { day: "Mon", day_ta: "திங்கள்", high: 31, low: 24, condition: "Light Rain", condition_ta: "லேசான மழை", rainProb: 70 },
        { day: "Tue", day_ta: "செவ்வாய்", high: 30, low: 24, condition: "Thunderstorms", condition_ta: "இடிமின்னல் மழை", rainProb: 85 },
        { day: "Wed", day_ta: "புதன்", high: 29, low: 23, condition: "Showers", condition_ta: "மழை", rainProb: 75 },
        { day: "Thu", day_ta: "வியாழன்", high: 31, low: 24, condition: "Cloudy", condition_ta: "மேகமூட்டம்", rainProb: 30 },
        { day: "Fri", day_ta: "வெள்ளி", high: 32, low: 25, condition: "Partly Cloudy", condition_ta: "பகுதி மேகமூட்டம்", rainProb: 20 }
      ]
    },
    "Nagapattinam": {
      name_ta: "நாகப்பட்டினம்",
      zone: "Coastal Delta Zone",
      zone_ta: "கடற்கரை டெல்டா மண்டலம்",
      typicalSoil: "Coastal Saline",
      avgRainfall: 1350,
      currentWeather: {
        temp: 29.5,
        humidity: 86,
        rainfall: 8.0,
        condition: "Overcast",
        condition_ta: "அடர் மேகமூட்டம்",
        windSpeed: 21,
        uvIndex: 5,
        dewPoint: 25.8
      },
      forecast: [
        { day: "Mon", day_ta: "திங்கள்", high: 30, low: 25, condition: "Breezy Rain", condition_ta: "காற்றுடன் மழை", rainProb: 80 },
        { day: "Tue", day_ta: "செவ்வாய்", high: 29, low: 24, condition: "Heavy Rain", condition_ta: "கனமழை", rainProb: 90 },
        { day: "Wed", day_ta: "புதன்", high: 30, low: 24, condition: "Showers", condition_ta: "மழை", rainProb: 65 },
        { day: "Thu", day_ta: "வியாழன்", high: 31, low: 25, condition: "Overcast", condition_ta: "மேகமூட்டம்", rainProb: 40 },
        { day: "Fri", day_ta: "வெள்ளி", high: 32, low: 26, condition: "Partly Cloudy", condition_ta: "பகுதி மேகமூட்டம்", rainProb: 25 }
      ]
    },
    "Mayiladuthurai": {
      name_ta: "மயிலாடுதுறை",
      zone: "Cauvery Delta Zone",
      zone_ta: "காவிரி டெல்டா மண்டலம்",
      typicalSoil: "Alluvial",
      avgRainfall: 1200,
      currentWeather: {
        temp: 31.0,
        humidity: 80,
        rainfall: 3.8,
        condition: "Partly Cloudy",
        condition_ta: "பகுதி மேகமூட்டம்",
        windSpeed: 15,
        uvIndex: 7,
        dewPoint: 24.6
      },
      forecast: [
        { day: "Mon", day_ta: "திங்கள்", high: 32, low: 24, condition: "Partly Cloudy", condition_ta: "மேகமூட்டம்", rainProb: 30 },
        { day: "Tue", day_ta: "செவ்வாய்", high: 31, low: 24, condition: "Rain Showers", condition_ta: "மழை", rainProb: 75 },
        { day: "Wed", day_ta: "புதன்", high: 30, low: 23, condition: "Scattered Rain", condition_ta: "சிதறிய மழை", rainProb: 60 },
        { day: "Thu", day_ta: "வியாழன்", high: 32, low: 24, condition: "Clear Sky", condition_ta: "தெளிவான வானம்", rainProb: 15 },
        { day: "Fri", day_ta: "வெள்ளி", high: 33, low: 25, condition: "Sunny", condition_ta: "வெயில்", rainProb: 10 }
      ]
    },
    "Cuddalore": {
      name_ta: "கடலூர்",
      zone: "North Eastern Coastal Zone",
      zone_ta: "வடகிழக்கு கடற்கரை மண்டலம்",
      typicalSoil: "Clayey",
      avgRainfall: 1200,
      currentWeather: {
        temp: 32.0,
        humidity: 76,
        rainfall: 2.1,
        condition: "Sunny",
        condition_ta: "வெயில்",
        windSpeed: 13,
        uvIndex: 8,
        dewPoint: 23.9
      },
      forecast: [
        { day: "Mon", day_ta: "திங்கள்", high: 33, low: 25, condition: "Sunny", condition_ta: "வெயில்", rainProb: 10 },
        { day: "Tue", day_ta: "செவ்வாய்", high: 32, low: 24, condition: "Partly Cloudy", condition_ta: "மேகமூட்டம்", rainProb: 40 },
        { day: "Wed", day_ta: "புதன்", high: 31, low: 24, condition: "Light Rain", condition_ta: "லேசான மழை", rainProb: 55 },
        { day: "Thu", day_ta: "வியாழன்", high: 32, low: 25, condition: "Clear Sky", condition_ta: "தெளிவான வானம்", rainProb: 20 },
        { day: "Fri", day_ta: "வெள்ளி", high: 34, low: 26, condition: "Sunny", condition_ta: "வெயில்", rainProb: 10 }
      ]
    },
    "Madurai": {
      name_ta: "மதுரை",
      zone: "Southern Zone",
      zone_ta: "தென் மண்டலம்",
      typicalSoil: "Red Loam",
      avgRainfall: 850,
      currentWeather: {
        temp: 34.2,
        humidity: 62,
        rainfall: 0.0,
        condition: "Hot & Sunny",
        condition_ta: "மிக்க வெயில்",
        windSpeed: 11,
        uvIndex: 9,
        dewPoint: 21.0
      },
      forecast: [
        { day: "Mon", day_ta: "திங்கள்", high: 35, low: 26, condition: "Sunny", condition_ta: "வெயில்", rainProb: 5 },
        { day: "Tue", day_ta: "செவ்வாய்", high: 35, low: 25, condition: "Clear Sky", condition_ta: "தெளிவான வானம்", rainProb: 10 },
        { day: "Wed", day_ta: "புதன்", high: 34, low: 25, condition: "Partly Cloudy", condition_ta: "பகுதி மேகமூட்டம்", rainProb: 20 },
        { day: "Thu", day_ta: "வியாழன்", high: 33, low: 24, condition: "Scattered Clouds", condition_ta: "மேகங்கள்", rainProb: 25 },
        { day: "Fri", day_ta: "வெள்ளி", high: 34, low: 25, condition: "Sunny", condition_ta: "வெயில்", rainProb: 10 }
      ]
    },
    "Tiruchirappalli": {
      name_ta: "திருச்சிராப்பள்ளி",
      zone: "Cauvery Mid-Delta Zone",
      zone_ta: "மத்திய காவிரி மண்டலம்",
      typicalSoil: "Alluvial",
      avgRainfall: 900,
      currentWeather: {
        temp: 33.1,
        humidity: 68,
        rainfall: 0.5,
        condition: "Clear Sky",
        condition_ta: "தெளிவான வானம்",
        windSpeed: 12,
        uvIndex: 8,
        dewPoint: 22.4
      },
      forecast: [
        { day: "Mon", day_ta: "திங்கள்", high: 34, low: 25, condition: "Clear Sky", condition_ta: "தெளிவான வானம்", rainProb: 10 },
        { day: "Tue", day_ta: "செவ்வாய்", high: 33, low: 24, condition: "Partly Cloudy", condition_ta: "மேகமூட்டம்", rainProb: 35 },
        { day: "Wed", day_ta: "புதன்", high: 32, low: 24, condition: "Light Rain", condition_ta: "லேசான மழை", rainProb: 45 },
        { day: "Thu", day_ta: "வியாழன்", high: 33, low: 25, condition: "Clear Sky", condition_ta: "தெளிவான வானம்", rainProb: 15 },
        { day: "Fri", day_ta: "வெள்ளி", high: 34, low: 25, condition: "Sunny", condition_ta: "வெயில்", rainProb: 5 }
      ]
    },
    "Tirunelveli": {
      name_ta: "திருநெல்வேலி",
      zone: "Tamirabarani Basin Zone",
      zone_ta: "தாமிரபரணி ஆற்றுப்படுகை மண்டலம்",
      typicalSoil: "Clayey",
      avgRainfall: 800,
      currentWeather: {
        temp: 32.8,
        humidity: 65,
        rainfall: 0.0,
        condition: "Sunny",
        condition_ta: "வெயில்",
        windSpeed: 18,
        uvIndex: 8,
        dewPoint: 21.8
      },
      forecast: [
        { day: "Mon", day_ta: "திங்கள்", high: 33, low: 25, condition: "Sunny", condition_ta: "வெயில்", rainProb: 10 },
        { day: "Tue", day_ta: "செவ்வாய்", high: 33, low: 24, condition: "Breezy", condition_ta: "தென்றல் காற்று", rainProb: 15 },
        { day: "Wed", day_ta: "புதன்", high: 32, low: 24, condition: "Partly Cloudy", condition_ta: "மேகமூட்டம்", rainProb: 30 },
        { day: "Thu", day_ta: "வியாழன்", high: 32, low: 24, condition: "Clear", condition_ta: "தெளிவு", rainProb: 10 },
        { day: "Fri", day_ta: "வெள்ளி", high: 33, low: 25, condition: "Sunny", condition_ta: "வெயில்", rainProb: 5 }
      ]
    }
  },

  // TNAU Standard Recommended Nutrients (kg/ha) per season
  tnauBaselines: {
    "Kuruvai": { N: 120, P: 40, K: 40, durationDays: 105, optimalYield: 4800 },
    "Samba": { N: 150, P: 50, K: 50, durationDays: 135, optimalYield: 5200 },
    "Thaladi": { N: 150, P: 50, K: 50, durationDays: 130, optimalYield: 4900 },
    "Navarai": { N: 120, P: 40, K: 40, durationDays: 115, optimalYield: 4500 }
  },

  // Realistic Historical Records
  sampleHistory: [
    {
      id: "AGRI-2026-081",
      date: "2026-10-12",
      district: "Thanjavur",
      season: "Samba",
      soilType: "Alluvial",
      area: 3.2,
      predictedYield: 4650,
      predictedQuintals: 46.5,
      actualYield: 4520,
      confidence: "91%",
      healthScore: 88,
      status: "Harvested"
    },
    {
      id: "AGRI-2026-077",
      date: "2026-09-28",
      district: "Tiruvarur",
      season: "Kuruvai",
      soilType: "Clayey",
      area: 2.0,
      predictedYield: 4320,
      predictedQuintals: 43.2,
      actualYield: 4380,
      confidence: "89%",
      healthScore: 84,
      status: "Harvested"
    },
    {
      id: "AGRI-2026-064",
      date: "2026-09-14",
      district: "Nagapattinam",
      season: "Kuruvai",
      soilType: "Coastal Saline",
      area: 4.5,
      predictedYield: 3890,
      predictedQuintals: 38.9,
      actualYield: 3810,
      confidence: "86%",
      healthScore: 78,
      status: "Harvested"
    },
    {
      id: "AGRI-2026-052",
      date: "2026-08-30",
      district: "Mayiladuthurai",
      season: "Kuruvai",
      soilType: "Alluvial",
      area: 1.8,
      predictedYield: 4720,
      predictedQuintals: 47.2,
      actualYield: 4680,
      confidence: "93%",
      healthScore: 92,
      status: "Harvested"
    },
    {
      id: "AGRI-2026-041",
      date: "2026-08-15",
      district: "Cuddalore",
      season: "Kuruvai",
      soilType: "Clayey",
      area: 2.5,
      predictedYield: 4210,
      predictedQuintals: 42.1,
      actualYield: 4150,
      confidence: "88%",
      healthScore: 82,
      status: "Harvested"
    },
    {
      id: "AGRI-2026-033",
      date: "2026-07-22",
      district: "Madurai",
      season: "Navarai",
      soilType: "Red Loam",
      area: 3.0,
      predictedYield: 3950,
      predictedQuintals: 39.5,
      actualYield: 4020,
      confidence: "87%",
      healthScore: 80,
      status: "Harvested"
    }
  ],

  // Common Paddy Pests and Diseases in Tamil Nadu
  pestAdvisory: [
    {
      id: "pest-1",
      name: "Rice Blast (Pyricularia oryzae)",
      name_ta: "நெல் குலை நோய்",
      risk: "Medium",
      risk_ta: "நடுத்தர அபாயம்",
      symptoms: "Spindle-shaped lesions with grey center and brownish border on leaf blades and nodes.",
      symptoms_ta: "இலைகளில் மையப்பகுதி சாம்பல் நிறமாகவும் ஓரங்கள் பழுப்பு நிறமாகவும் உள்ள கண் வடிவப் புள்ளிகள்.",
      preventive: "Avoid excessive urea application during cloudy/humid days. Maintain water film.",
      preventive_ta: "மேகமூட்டமான நாட்களில் அதிகப்படியான யூரியா இடுவதைத் தவிர்க்கவும். வயலில் நீர்த்தேக்கத்தை நிர்வகிக்கவும்.",
      organicAction: "Spray Pseudomonas fluorescens (0.2%) @ 2.5 kg/ha in 500L water.",
      organicAction_ta: "சூடோமோனாஸ் ஃபுளோரசன்ஸ் 0.2% (2.5 கிலோ/ஹெக்) தெளிக்கவும்."
    },
    {
      id: "pest-2",
      name: "Brown Planthopper (BPH - Nilaparvata lugens)",
      name_ta: "புகையான் பூச்சி",
      risk: "High",
      risk_ta: "அதிதீவிர அபாயம்",
      symptoms: "Circular yellowing patches that turn brown and dry like hopper burn at basal tillers.",
      symptoms_ta: "பயிர்களின் அடிப்பகுதியில் கூட்டம் கூட்டமாகச் சாறு உறிஞ்சுவதால் வட்ட வடிவில் காய்ந்து பதராவது.",
      preventive: "Drain field water completely for 3-4 days (AWD practice). Avoid synthetic pyrethroids.",
      preventive_ta: "வயல் நீரை 3-4 நாட்களுக்கு வடித்துவிடவும். தேவையான இடைவெளியில் காற்றோட்டம் வழங்கவும்.",
      organicAction: "Apply Neem Seed Kernel Extract (NSKE 5%) or Neem Oil (3%).",
      organicAction_ta: "வேப்பங்கொட்டை சாறு 5% அல்லது வேப்பெண்ணெய் 3% தெளிக்கவும்."
    },
    {
      id: "pest-3",
      name: "Yellow Stem Borer (Scirpophaga incertulas)",
      name_ta: "மஞ்சள் தண்டு துளைப்பான்",
      risk: "Low",
      risk_ta: "குறைந்த அபாயம்",
      symptoms: "Dead hearts during vegetative stage and white ears (chaffy panicles) at heading stage.",
      symptoms_ta: "பயிர் வளர்ச்சியில் குருத்துக்காய்வு மற்றும் கதிர் பருவத்தில் வெண்கதிர் தோன்றுதல்.",
      preventive: "Install pheromone traps @ 12 traps/ha for monitoring moth flight.",
      preventive_ta: "ஹெக்டேருக்கு 12 இனக்கவர்ச்சிப் பொறிகளை அமைத்து அந்துப்பூச்சிகளைக் கண்காணிக்கவும்.",
      organicAction: "Release egg parasitoid Trichogramma japonicum @ 100,000/ha twice at weekly intervals.",
      organicAction_ta: "டிரைக்கோடெர்மா ஒட்டுண்ணியை வார இடைவெளியில் ஹெக்டேருக்கு 1 லட்சம் வீதம் விடவும்."
    }
  ]
};

window.AGRI_DATA = AGRI_DATA;

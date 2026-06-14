class DiseaseResult {
  final String diseaseName;
  final double confidence;
  final String description;
  final List<String> medicines;
  final List<String> preventionTips;
  final String severity; // Low, Medium, High

  DiseaseResult({
    required this.diseaseName,
    required this.confidence,
    required this.description,
    required this.medicines,
    required this.preventionTips,
    required this.severity,
  });
}

class DiseaseDetectionData {
  static DiseaseResult getMockResult() {
    return DiseaseResult(
      diseaseName: 'Tomato Early Blight',
      confidence: 0.94,
      description: 'A common fungal disease caused by Alternaria solani. It affects leaves, stems, and fruits.',
      severity: 'Medium',
      medicines: [
        'Chlorothalonil Fungicide',
        'Copper-based sprays',
        'Mancozeb'
      ],
      preventionTips: [
        'Rotate crops every 2-3 years.',
        'Prune lower leaves to improve air circulation.',
        'Apply mulch to prevent soil splashing onto leaves.',
        'Water at the base of the plant, not on leaves.'
      ],
    );
  }
}

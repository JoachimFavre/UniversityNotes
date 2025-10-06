from lib.course import Course

class CourseList:
    # BA1
    ANALYSE_1 = Course(is_bachelor=True, semester=1, name="Analyse-1")
    ALGEBRE_LINEAIRE = Course(is_bachelor=True, semester=1, name="AlgebreLinaire")
    AICC_1 = Course(is_bachelor=True, semester=1, name="AICC-1")

    # BA2
    AICC_2 = Course(is_bachelor=True, semester=2, name="AICC-2")
    ANALYSE_2 = Course(is_bachelor=True, semester=2, name="Analyse-2")
    ANALYSE_2_METHODES_DE_DEMONSTRATION = Course(is_bachelor=True, semester=2, name="Analyse-2-MethodesDeDemonstration")
    DIGITAL_SYSTEM_DESIGN = Course(is_bachelor=True, semester=2, name="DigitalSystemDesign")
    
    # BA3
    ALGORITHMS_1 = Course(is_bachelor=True, semester=3, name="Algorithms-1")
    ANALYSE_3 = Course(is_bachelor=True, semester=3, name="Analyse-3")
    COMPUTER_NETWORKS = Course(is_bachelor=True, semester=3, name="ComputerNetworks")
    INTRO_TO_MACHINE_LEARNING_BA3 = Course(is_bachelor=True, semester=3, name="IntroToMachineLearning-BA3-Summary", is_summary=True)
    NUMERICAL_METHODS = Course(is_bachelor=True, semester=3, name="NumericalMethods")
    
    # BA4
    ANALYSE_4 = Course(is_bachelor=True, semester=4, name="Analyse-4")
    PROBABILITY_AND_STATISTICS = Course(is_bachelor=True, semester=4, name="ProbabilityAndStatistics")
    SIGNALS_AND_SYSTEMS = Course(is_bachelor=True, semester=4, name="SignalsAndSystems")
    THEORY_OF_COMPUTATION = Course(is_bachelor=True, semester=4, name="TheoryOfComputation")
    
    # BA5
    ALGEBRA = Course(is_bachelor=True, semester=5, name="Algebra")
    INTRO_TO_QUANTUM_INFORMATION_PROCESSING = Course(is_bachelor=True, semester=5, name="IntroToQuantumInformationProcessing-Summary", is_summary=True)
    
    # BA6
    INTRO_TO_QUANTUM_COMPUTATION = Course(is_bachelor=True, semester=6, name="IntroToQuantumComputation-Summary", is_summary=True)
    
    # MA1
    ALGORITHMS_2 = Course(is_bachelor=False, semester=1, name="Algorithms-2")
    COMPUTATIONAL_COMPLEXITY = Course(is_bachelor=False, semester=1, name="ComputationalComplexity")
    QUANTUM_PHYSICS_2 = Course(is_bachelor=False, semester=1, name="QuantumPhysics-2")

    # MA2 
    COMPUTATIONAL_QUANTUM_PHYSICS = Course(is_bachelor=False, semester=2, name="ComputationalQuantumPhysics")
    QUANTUM_INFORMATION_THEORY = Course(is_bachelor=False, semester=2, name="QuantumInformationTheory")
    SUBLINEAR_ALGORITHMS = Course(is_bachelor=False, semester=2, name="SublinearAlgorithms")

    # MA3
    INFORMATION_THEORY_AND_CODING = Course(is_bachelor=False, semester=3, name="InformationTheoryAndCoding")
    INTRO_TO_QUANTUM_CRYPTOGRAPHY = Course(is_bachelor=False, semester=3, name="IntroToQuantumCryptography")
    
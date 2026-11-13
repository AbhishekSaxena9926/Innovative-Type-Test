8-BIT MINI PROCESSOR DESIGN AND SIMULATION

Student: Abhishek Saxena
Course: M.Tech (CS)
Subject: Digital Electronics & Computer Organization
Subject Code: PCS1001
Roll Number: 2020610101070005
Submitted to: Prabhat Srivastava, Faculty, Digital Electronics & Computer Organization (PCS1001)

PROJECT OVERVIEW
This project presents the architecture and instruction-level functional simulation of a compact 8-bit accumulator-based mini processor. It includes a 4-bit program counter, 8-bit instruction register, accumulator, ALU, control unit, 16 x 8-bit program ROM, 16 x 8-bit data RAM, output register, and Zero/Carry status flags.

FILES
- 8-Bit_Mini_Processor_Presentation.pptx : 18-slide presentation
- 8-Bit_Mini_Processor_Project_Report.docx : editable project report
- 8-Bit_Mini_Processor_Project_Report.pdf : report in PDF format
- 8bit_processor_sim.py : standalone Python functional simulator

RUN THE SIMULATOR
Requires Python 3. Run:
    python 8bit_processor_sim.py

The program prints the sample instruction trace and executes six self-tests. The sample program stores 5, adds 3, stores the result, subtracts 5, and sends the final value (3 / 0x03) to the output register.

SIMULATION SCOPE
This is an instruction-level functional software simulation. It demonstrates the CPU's instruction execution and register/memory state changes. It is not a transistor-level, gate-level timing, or FPGA implementation.

BEFORE SUBMISSION
1. Create your own GitHub repository and upload the PPT, report, and simulator source file.
2. Replace the GitHub repository URL placeholder on the PPT cover/conclusion slides and in the report with the actual repository URL.
3. Ensure the repository is accessible to the evaluator.
4. Submit the PPT and report to Prabhat Srivastava through the required Google Classroom workflow.

Do not submit the documents with the GitHub URL placeholder still present.

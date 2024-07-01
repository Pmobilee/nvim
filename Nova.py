# ====================================================================================
# COPYRIGHT NOTICE
# ====================================================================================
# This software and its source code are proprietary and confidential to Nova 23 B.V.
# Unauthorized copying of this file, via any medium, and the underlying code, is
# strictly prohibited.

# ====================================================================================
# LICENSE AGREEMENT
# ====================================================================================
# This code is part of a larger software package and governed by the license terms
# provided by Nova 23 B.V. Use, modification, distribution, and/or reproduction of this
# software and its code are subject to the terms of the applicable license agreement.
# Please refer to the license agreement for specific restrictions and permissions.

# ====================================================================================
# DISCLAIMER
# ====================================================================================
# This software is provided by Nova 23 B.V. "as is" and any express or implied warranties,
# including, but not limited to, the implied warranties of merchantability and fitness
# for a particular purpose are disclaimed. In no event shall Nova 23 B.V. be liable for
# any direct, indirect, incidental, special, exemplary, or consequential damages
# (including, but not limited to, procurement of substitute goods or services; loss of
# use, data, or profits; or business interruption) however caused and on any theory of
# liability, whether in contract, strict liability, or tort (including negligence or
# otherwise) arising in any way out of the use of this software, even if advised of the
# possibility of such damage.

# ====================================================================================
# CONTACT INFORMATION
# ====================================================================================
# For any inquiries regarding this software, please contact Nova 23 B.V. at:
# Company Owners: Nova_AI@hotmail.com
# Developer:      Damion.woods1996@gmail.com

# ====================================================================================
# ACKNOWLEDGEMENTS
# ====================================================================================
# This software may include or incorporate third-party components with separate
# copyright and licensing notices located in accompanying documentation or other materials
# associated with the software. Users are obliged to review and comply with the respective
# copyright and licensing terms of these components.


import argparse
import json
import logging
import os
import subprocess
import traceback
import uuid
from datetime import datetime

import colorlog
import older_modules.DSM as DSM
import psychological_tests.guidelines as guidelines
import psychological_tests.test_utilities as test_utilities
from modules.Commands import Commands
from modules.ConversationManager import ConversationManager
from modules.Diagnosis_categorical import DiagnoseCategorical
from modules.Diagnosis_criteria import DiagnoseCriteria
from modules.Intake import Intake
from modules.Report import Report
from modules.Summaries import Summaries
from modules.Utilities import Utilities

# import old.report_util as report_util
cwd = os.getcwd()
try:
    os.chdir("NOVA/")
except:
    pass


def update_args_from_config(file_path, args):
    with open(file_path, "r") as file:
        config = json.load(file)

    # Check and add/update values from the config to the args
    for key, value in config.items():
        setattr(args, key, value)


def main(args):

    # Create a formatter for colored output
    formatter = colorlog.ColoredFormatter(
            "%(log_color)s%(asctime)s - %(levelname)s - %(message)s\n        log_colors={
                "DEBUG": "white",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold_red",
                },
            ) 

    test= {"teh":"sre", "dfsd":"fsdf"}
    # Create a console handler with the colored formatter
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # Create a unique log file name
    log_filename = (
            f"{args.user_id}_{args.chat_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            )
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    log_filepath = os.path.join(log_dir, log_filename)

    # Create a file handler without colors
    file_handler = logging.FileHandler(log_filepath)
    file_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            )

    # Get the root logger and set its handlers
    logger = logging.getLogger()
    logger.setLevel(args.logging)
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    logging.debug("Task: %s, Args: %s", args.task, args)

    utilities = Utilities()
    manager = ConversationManager(args)
    commands = Commands(manager, utilities)
    summaries = Summaries(manager, utilities, commands)
    report = Report(manager, utilities, commands)
    intake = Intake(manager, utilities, commands)
    diagnose_criteria = DiagnoseCriteria(manager, utilities, commands, report)
    diagnose_categorical = DiagnoseCategorical(manager, utilities, commands, report)
    manager.set_commands_instance(commands)
    manager.set_utilities_instance(utilities)

    if manager.args.recognition_model == "whisper":
        manager.whisper.setup_model("distil-large-v2")
    if manager.args.gaze_tracking:
        from GazeTracking.Gaze import GazeTracker

        gaze = GazeTracker()
        gaze.start_calibration()
        intake.setup_gaze(gaze)

    if manager.args.config:
        logging.debug("Using config file")
        update_args_from_config(manager.args.config, manager.args)
        update_args_from_config(args.config, args)  # just a backup
        manager.chat_id = manager.args.chat_id
        manager.user_id = manager.args.user_id  # quick fix, TODO
        manager.NAME = manager.args.name

    if manager.args.task == "update_commands":
        logging.debug("Updating commands")
        commands.create_db(delete_table=True)
        commands.update_db_from_file()

    if manager.args.chat_id == "latest":
        if manager.args.task != "intake":
            manager.chat_id = utilities.get_highest_chat_id(
                    manager.args.user_id,
                    manager.tables["report_data"],
                    args.database,
                    manager,
                    )
            manager.args.chat_id = utilities.get_highest_chat_id(
                    manager.args.user_id,
                    manager.tables["report_data"],
                    args.database,
                    manager,
                    )
        else:

            manager.chat_id = utilities.get_highest_chat_id(
                    manager.args.user_id,
                    manager.tables["intakes"],
                    manager.args.database,
                    manager,
                    )
            manager.args.chat_id = utilities.get_highest_chat_id(
                    manager.args.user_id,
                    manager.tables["intakes"],
                    manager.args.database,
                    manager,
                    )

    if manager.args.user_id == "None":
        manager.args.user_id = str(uuid.uuid4())
        logging.debug("Created user id: %s", manager.args.user_id)

    diagnose_criteria.create_folder_structure(
            ".", str(manager.args.user_id), str(manager.args.chat_id)
            )



    if manager.args.task == "server":
        # """
        # Run the server in a subprocess. This is no longer necessary, but kept for legacy reasons.
        # """

        gpu_args = [
                "-m",
                manager.args.model,
                "-p",
                manager.args.port,
                "-d",
                manager.args.device,
                ]
        gpu_args = [str(arg) for arg in gpu_args]
        logging.debug(
                "Running model %s on port %s", manager.args.model, manager.args.port
                )
        subprocess.run(["python", "GPU_api.py"] + gpu_args)

    elif manager.args.task == "generate_intake_report_summaries":
        # """
        # This is the main function for summarizing conversations. Given the conversation manager holds a specific user_id/chat_id pair,
        # will summarize the conversation for that specific user.
        # By default, this will use the quick summarization method, if not otherwise specified by the 'mode' argument.
        # """

        user_dataframe = utilities.get_user_data(
                manager.user_id,
                manager.args.chat_id,
                manager.DB_PATH,
                manager.tables["intakes"],
                manager,
                )
        summaries.summarize_conversations(user_dataframe)

    elif manager.args.task == "generate_intake_report_tracking_summaries":
        user_dataframe = utilities.get_user_data(
                manager.user_id,
                manager.args.chat_id,
                manager.DB_PATH,
                manager.tables["intakes"],
                manager,
                )

        summaries.summarize_conversations_with_tracking(user_dataframe)

    elif manager.args.task == "generate_intake_report_data":

        user_dataframe = utilities.get_user_data(
                user_id=manager.user_id,
                chat_id=manager.chat_id,
                db_filename=manager.DB_PATH,
                table_name=manager.tables["report_data"],
                manager=manager,
                )
        report.generate_report_data(user_dataframe)

    elif manager.args.task == "generate_intake_report":
        # '''
        # This is the main function for generating an intake report, not including any disorder or diagnostic report.
        # Given the conversation manager holds a specific user_id/chat_id pair, will generate a report for that specific user.
        # The conversation needs to have been summarized previously.
        # '''

        user_dataframe = utilities.get_user_data(
            user_id=manager.user_id,
            chat_id=manager.chat_id,
            db_filename=manager.DB_PATH,
            table_name=manager.tables["report_data"],
            manager=manager,
        )

        logging.debug(user_dataframe)

        report_data = {}
        report_data["Name_Patient"] = manager.args.name
        report_data["Location"] = "Amsterdam"
        report_data["Title"] = "Nova23 Casus"
        report_data["Case_Number"] = "212"
        report_data["Institution"] = "Nova23"
        report_data["Supervisor"] = "Nova"
        report_data["Registration_Number"] = "02124388525"

        report.generate_pdf(manager.args.file_report, user_dataframe, report_data)

    elif manager.args.task == "fill_icd":
        # '''
        # This is a one-time function for filling the ICD database, or updating it if necessary.
        # '''
        subprocess.run(["python", "ICD_api.py"])

    elif manager.args.task == "fill_dsm":
        # '''
        # This is a one-time function for filling the DSM database.
        # '''
        subprocess.run(["python", "DSM.py"])

    elif manager.args.task == "diagnose_categorical":
        # '''
        # A legacy function for diagnosing a patient. Uses the ICD/DSM categories to narrow down diagnoses. Does not take into account any diagnostic criteria.
        # '''

        # utilities.change_model("mistral8")
        diagnose_categorical.diagnose_using_categories()

    elif manager.args.task == "diagnose_using_criteria":
        # '''
        # A more recent function for diagnosing a patient, uses the diagnostic criteria to narrow down diagnoses.
        # '''
        # diagnose.create_criteria_report()

        diagnose_criteria.diagnose_using_criteria()

    elif manager.args.task == "criteria_report":
        # Will generate a report based on the diagnostic criteria from the DSM.
        diagnose_criteria.create_criteria_report()

    elif args.task == "intake":
        # Performs the main intake conversation.

        logging.debug("latest Chat ID of INTAKES: %s", str(manager.args.chat_id))
        manager.chat_id = manager.args.chat_id
        manager.set_topics()
        intake.intake()

    elif manager.args.task == "disorder_reports_categorical":
        if manager.args.chat_id == "latest":
            manager.chat_id = utilities.get_highest_chat_id(
                manager.args.user_id,
                manager.tables["report_data"],
                args.database,
                manager,
            )
        report.generate_disorder_pdfs()

    elif manager.args.task == "explain_disorders_categorical":
        if manager.args.chat_id == "latest":
            manager.chat_id = utilities.get_highest_chat_id(
                manager.args.user_id,
                manager.tables["report_data"],
                manager.args.database,
                manager,
            )
        diagnose_categorical.explain_disorders()

    elif manager.args.task == "dsm_backstory":
        from older_modules.old_Utilities import old_Utilities

        old_Utilities.dsm_to_backstory(manager=manager)

    elif manager.args.task == "fill_fake_speech_time":
        from older_modules.old_Utilities import old_Utilities

        old_Utilities.fill_fake_speech_time(manager)

    elif manager.args.task == "create_criteria_questions":
        DSM.create_dsm_criteria_questions(manager, utilities, commands)

    elif manager.args.task == "ask_criteria_questions":
        intake.check_unsure_criteria()

    elif manager.args.task == "perform_diagnostic_test":
        import importlib

        test_utils = test_utilities.test_utilities(manager, utilities, commands)
        test_utils.info(message="Starting test module for " + manager.args.test)

        module_name = manager.args.test

        try:
            # Import the specified module dynamically
            module = importlib.import_module("psychological_tests." + module_name)
            # Get the class with the same name as the modul
            test = {"hey" : "tooo"}
            module_class = getattr(module, module_name)
            # Instantiate the class
            module_instance = module_class(manager, utilities, commands)

        except ModuleNotFoundError:
            logging.error("Module '%s' not found.", module_name, exc_info=True)
        else:
            if (
                    hasattr(manager.args, "assessment_only")
                    and manager.args.assessment_only
                    ):
                if hasattr(module_instance, "diagnose") and callable(
                        module_instance.diagnose
                        ):
                    # If assessment_only is True and the module has a diagnose method, call it
                    module_instance.diagnose()
                else:
                    logging.error("Module '%s' does not have a diagnose method.")
            else:
                try:
                    if hasattr(module_instance, "perform_test") and callable(
                            module_instance.perform_test
                            ):
                        # If assessment_only is False or not provided and the module has a perform_test method, call it
                        module_instance.perform_test()
                    else:
                        logging.error(
                                "Class '%s' in module '%s' does not have a perform_test method.\n\n%s",
                                module_class,
                                module_name,
                                traceback.format_exc(),
                                )

                except AttributeError:
                    logging.error(
                            "Class '%s' not found in module '%s'.",
                            module_class,
                            module_name,
                            exc_info=True,
                            )

    elif manager.args.task == "fill_apa":
        logging.debug("Creating APA table")
        apa = guidelines.APA(manager, utilities, commands)
        # apa.create_table()
        logging.debug("Inserting guidelines")
        apa.insert_guidelines()

    elif manager.args.task == "deprecated_generate_nova_advisory_guidelines":
        disorder = manager.args.disorder
        try:
            manager.args.disorder = disorder
            apa = guidelines.APA(manager, utilities, commands)
            if manager.args.short_guidelines:
                apa.give_guidelines_short(types=manager.args.guideline_types)
            else:
                apa.give_guidelines(types=manager.args.guideline_types)
        except Exception:
            logging.error("Error with disorder: %s", disorder, exc_info=True)

    elif manager.args.task == "insert_compact_guidelines":
        logging.debug("Creating compact APA Data")
        apa = guidelines.APA(manager, utilities, commands)
        apa.insert_compact_guidelines()

    elif manager.args.task == "diagnostic_test_report":
        test_utils = test_utilities.test_utilities(manager, utilities, commands)
        test_utils.create_pdf_report()

    elif manager.args.task == "generate_compacted_nova_advisory_guidelines":
        logging.debug("Creating compact APA Data")
        apa = guidelines.APA(manager, utilities, commands)
        apa.generate_compact_guidelines(types=manager.args.guideline_types)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Create a chatbot character.")
    parser.add_argument("-n", "--name", help="Specify client's name", default="Robert")
    parser.add_argument(
        "-t",
        "--task",
        choices=[
            "explain_disorders_categorical",
            "full_tryout",
            "disorder_reports_categorical",
            "diagnose_categorical",
            "fill_dsm",
            "fill_icd",
            "generate_intake_report",
            "intake",
            "generate_intake_report_summaries",
            "generate_intake_report_tracking_summaries",
            "update_commands",
            "server",
            "generate_intake_report_data",
            "diagnose_using_criteria",
            "criteria_report",
            "dsm_backstory",
            "fill_fake_speech_time",
            "create_criteria_questions",
            "ask_criteria_questions",
            "perform_diagnostic_test",
            "fill_apa",
            "deprecated_generate_nova_advisory_guidelines",
            "diagnostic_test_report",
            "insert_compact_guidelines",
            "generate_compacted_nova_advisory_guidelines",
        ],
        help="Specify the task to run",
    )
    parser.add_argument("-a", "--age", help="Specify an age", type=int, default=27)
    parser.add_argument("-au", "--auto", action="store_true")
    parser.add_argument(
        "-c",
        "--check",
        help="Check if question is already discussed?",
        action="store_true",
    )
    parser.add_argument(
        "-db",
        "--database",
        help="Specify database location",
        default="databases/conversation.db",
    )
    parser.add_argument(
        "-dt",
        "--database_type",
        help="Specify database type",
        default="sqlite",
    )
    parser.add_argument(
        "-ct",
        "--context",
        help="Keep track of conv context at the cost of tokens?",
        action="store_true",
        default=True,
    )
    parser.add_argument("-u", "--user_id", help="User UID", type=str, default="1001")
    parser.add_argument("-ci", "--chat_id", help="Specify chat_id", default="latest")
    parser.add_argument(
        "-tc", "--table_commands", help="User UID", type=str, default="commands"
    )
    parser.add_argument(
        "-ti", "--table_intakes", help="User UID", type=str, default="intakes"
    )
    parser.add_argument(
        "-trs",
        "--table_report_summaries",
        help="report summaries table name",
        type=str,
        default="report_summaries",
    )
    parser.add_argument(
        "-trd",
        "--table_report_data",
        help="report table name",
        type=str,
        default="report_data",
    )
    parser.add_argument(
        "-fc",
        "--file_commands",
        help="User UID",
        type=str,
        default="./databases/GENERAL.json",
    )
    parser.add_argument(
        "-fr",
        "--file_report",
        help="folder to generate report to",
        type=str,
        default="./reports",
    )
    parser.add_argument("-m", "--model", help="specify model", default="mistral8")
    parser.add_argument("--model_type", help="specify model type", default="wizard")
    parser.add_argument(
        "-mo", "--mode", help="specify mode of generating report", default="quick"
    )
    parser.add_argument("-p", "--port", help="portnumber", default=5000)
    parser.add_argument("-d", "--device", help="CPU/GPU", default="GPU")
    parser.add_argument("-sp", "--speech", action="store_true")
    parser.add_argument(
        "--sex",
        type=str,
        required=False,
        choices=["male", "female"],
        default="No Gender Specified",
    )
    parser.add_argument("-wu", "--webui", action="store_true")
    parser.add_argument("-ex", "--extra_information", type=str, default="")
    parser.add_argument("-sh", "--short_intake", action="store_true")
    parser.add_argument("-rg", "--report_graphs", action="store_true")
    parser.add_argument("-l", "--language", help="specify language", default="en-US")
    parser.add_argument("-im", "--intro_message", action="store_true")
    parser.add_argument("-rs", "--rolling_summary", action="store_true")
    parser.add_argument("-ft", "--fresh_test", action="store_true")
    parser.add_argument("-fd", "--fresh_diagnose", action="store_true")
    parser.add_argument(
        "-tst",
        "--test",
        choices=[
            "CAPS5",
            "BDI",
            "PHQ",
            "PHQ_4",
            "PHQ_8",
            "PHQ_9",
            "PHQ_15",
            "PHQ_brief",
            "PHQ_SADS",
            "GAD_7",
            "DIVA5",
            "DIVA5_ID",
            "MDQ",
            "MANSA",
            "YBOCS",
        ],
        help="Specify the test to run",
    )
    parser.add_argument("-ao", "--assessment_only", action="store_true")
    parser.add_argument("-pt", "--pause_threshold", type=float, default=1.5)
    parser.add_argument("-ta", "--test_answers", action="store_true")
    parser.add_argument("-do", "--disorder", type=str)
    parser.add_argument("-sg", "--short_guidelines", action="store_true", default=True)
    parser.add_argument("--guideline_types", nargs="+", default=["psychiatry", "NICE"])
    parser.add_argument("--describe_criteria_met_report", action="store_true")
    parser.add_argument("--config", help="Path to configuration file", type=str)
    parser.add_argument(
        "--recognition_model", default="google", choices=["google", "whisper"]
    )
    parser.add_argument("--num_last_words", type=int, default=None)
    parser.add_argument("--diagnosis_type", type=str, default="DSM")
    parser.add_argument("--logging", default="INFO")
    parser.add_argument("--avg_words_per_minute", type=int, default=150)
    parser.add_argument("--gaze_tracking", action="store_true")
    parser.add_argument("--intake_reasoning", action="store_true")
    parser.add_argument("--redo_last_intake_question_upon_failure", action="store_true")
    parser.add_argument("--db_type", default="sqlite")
    parser.add_argument("--cloud_config", default="config.json")
    parser.add_argument("--use_gguf_chat_template", action="store_true")

    args = parser.parse_args()
    main(args)

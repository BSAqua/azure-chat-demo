from approaches.flow.shared_states import State, StateExit, States, StateStartISP, StateStartPreperation, VariableDistressLevel, VariableExitText, VariableIsBotMale, VariableIsPatientMale, VariableIspPath, VariablePatientName
from approaches.requestcontext import RequestContext

StateGetDistressLevel = "GET_DISTRESS_LEVEL"
StateAskIfToContinueOnLowDistress = "ASK_IF_TO_CONTINUE_ON_LOW_DISTRESS"
StateAskWhatAnnoying = "ASK_WHAT_ANNOYING"
StateGetAnnoyingReason = "GET_ANNOYING_REASON"

async def start_preperation(request_context: RequestContext):
    is_patient_male = request_context.get_var(VariableIsPatientMale)
    patient_name = request_context.get_var(VariablePatientName)
    request_context.set_next_state(StateGetDistressLevel)
    return request_context.write_chat_message("""שלום {patient_name}, {welcome} לתהליך ייצוב מיידי, שמטרתו להביא לרגיעה ולהקלה במצוקה פסיכולוגית. תהליך זה עזר לאנשים רבים בעולם. התהליך ייקח כ 10-20 דקות לכל היותר, במהלכן אנחה אותך בשלבים חשובים של הרגעה
יש תרגיל שיכול לעזור לך. זה עזר לאנשים אחרים, זה יעזור לך להרגיש {calm} יותר. אבל לפני שנתחיל, {can_you} להגיד לי עד כמה {you} {annoyed} או חווה מצוקה כרגע (במספר)?
0  לא {annoyed} ולא חווה מצוקה כלל,
10 {annoyed} או חווה מצוקה ברמה חריפה""".format(
    patient_name = patient_name,
    welcome = "ברוך הבא" if is_patient_male else "ברוכה הבאה",
    calm = "רגוע" if is_patient_male else "רגועה",
    can_you = "אתה יכול" if is_patient_male else "את יכולה",
    you = "אתה" if is_patient_male else "את",
    annoyed = "מוטרד" if is_patient_male else "מוטרדת"))
States[StateStartPreperation] = State(is_wait_for_user_input_before_state=False, run=start_preperation)

async def get_distress_level(request_context: RequestContext):
    distress_msg = request_context.history[-1]["content"]
    distress = int(distress_msg)
    if 0 <= distress and distress <= 1:
        request_context.set_next_state(StateAskIfToContinueOnLowDistress)
        return request_context.write_chat_message("אני {understand} שאינך חווה מצוקה כרגע. האם תרצה לסיים את התהליך כעת?".format(understand = understand))
    elif 2 <= distress and distress <= 10:
        request_context.set_next_state(StateAskWhatAnnoying)
    else:
        return request_context.write_chat_message("לא הבנתי את תשובתך. אנא {type} מספר בין 0 ל-10".format(type = "הקלד" if request_context.get_var(VariableIsPatientMale) else "הקלידי"))
    request_context.save_to_var(VariableDistressLevel, distress)
States[StateGetDistressLevel] = State(run=get_distress_level)

async def ask_if_to_continue_on_low_distress(request_context: RequestContext):
    if request_context.history[-1]["content"] == "כן":
        request_context.set_next_state(StateExit)
        request_context.save_to_var(VariableExitText, "תודה, באפשרותך לחזור בשלב מאוחר יותר במידה {will_want}.".format(will_want = "ותרצה" if request_context.get_var(VariableIsPatientMale) else "ותרצי"))
    elif request_context.history[-1]["content"] == "לא":
        request_context.set_next_state(StateAskWhatAnnoying)
    else:
        return request_context.write_chat_message("לא הבנתי את תשובתך. אנא הקלד כן/לא")
States[StateAskIfToContinueOnLowDistress] = State(run=ask_if_to_continue_on_low_distress)

async def ask_what_annoying(request_context: RequestContext):
    request_context.set_next_state(StateGetAnnoyingReason)
    distress = request_context.get_var(VariableDistressLevel)
    is_patient_male = request_context.get_var(VariableIsPatientMale)
    if 2 <= distress and distress <= 10:
        understand = "מבין" if request_context.get_var(VariableIsBotMale) else "מבינה"
        prefixByDistressLevel = "אני {understand} {that_you} חווה {some}מצוקה כרגע, בשביל זה אני כאן".format(understand = understand, that_you = "שאתה" if is_patient_male else "שאת", some = "מידה מסוימת של " if distress <= 4 else "")
    else:
        prefixByDistressLevel = ""
    return request_context.write_chat_message(prefixByDistressLevel + """
מה הכי מטריד אותך כעת: 
1. אני {feel} כרגע בסכנה/{threatened}
2. אני {feel} {guilty_or_accountable} על משהו קשה שקרה
3. אני {feel} חוסר שליטה לגבי מה שקורה עכשיו
4. אני {feel} חוסר שליטה לגבי איומים או מצבים קשים שעלולים לקרות בעתיד
5. אני {concerned_and_feel} חוסר שליטה בנוגע לאנשים שיקרים לי.

שים לב, ייתכן שיותר מתשובה אחת משקפת את מה שאתה {feel}. {select} את זו שמשקפת בצורה הכי מדוייקת את מה {that_you_feel}""".format(
    feel = "מרגיש" if is_patient_male else "מרגישה",
    threatened = "מאויים" if is_patient_male else "מאויימת",
    guilty_or_accountable = "אשם או אחראי" if is_patient_male else "אשמה או אחראית",
    concerned_and_feel = "דואג וחש" if is_patient_male else "דואגת וחשה",
    select = "בחר" if is_patient_male else "בחרי",
    that_you_feel = "מה שאתה מרגיש" if is_patient_male else "מה שאת מרגישה",
))
States[StateAskWhatAnnoying] = State(is_wait_for_user_input_before_state=False, run=ask_what_annoying)

async def get_annoying_reason(request_context: RequestContext):
    isp_path = request_context.history[-1]["content"]
    if not(isp_path in ["1", "2", "3", "4", "5"]):
        return request_context.write_chat_message("לא הבנתי את תשובתך. אנא הקלד מספר בין 1 ל-5?")
    request_context.save_to_var(VariableIspPath, isp_path)
    request_context.set_next_state(StateStartISP)
States[StateGetAnnoyingReason] = State(run=get_annoying_reason)
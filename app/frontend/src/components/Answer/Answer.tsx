import { useMemo, useState } from "react";
import { Stack, IconButton } from "@fluentui/react";
import DOMPurify from "dompurify";

import styles from "./Answer.module.css";

import { ChatAppResponse, getCitationFilePath } from "../../api";
import { parseAnswerToHtml } from "./AnswerParser";
import { AnswerIcon } from "./AnswerIcon";

interface Props {
    answer: ChatAppResponse;
    isSelected?: boolean;
    isStreaming: boolean;
    onCitationClicked: (filePath: string) => void;
    onThoughtProcessClicked: () => void;
    onSupportingContentClicked: () => void;
    onEvaluationClicked: () => void;
    onGoodFeedbackClicked: () => void;
    onBadFeedbackClicked: () => void;
    onFollowupQuestionClicked?: (question: string) => void;
    showFollowupQuestions?: boolean;
}

export const Answer = ({
    answer,
    isSelected,
    isStreaming,
    onCitationClicked,
    onThoughtProcessClicked,
    onSupportingContentClicked,
    onEvaluationClicked,
    // onGoodFeedbackClicked,
    // onBadFeedbackClicked,
    onFollowupQuestionClicked,
    showFollowupQuestions
}: Props) => {
    const followupQuestions = answer.choices[0].context.followup_questions;
    const messageContent = answer.choices[0].message.content;
    const parsedAnswer = useMemo(() => parseAnswerToHtml(messageContent, isStreaming, onCitationClicked), [answer]);

    const sanitizedAnswerHtml = DOMPurify.sanitize(parsedAnswer.answerHtml);

    const [feedbackGiven, setFeedbackGiven] = useState<boolean>(false);

    const onGoodFeedbackClicked = () => {
        setFeedbackGiven(true);
    };

    const onBadFeedbackClicked = () => {
        setFeedbackGiven(true);
    };

    return (
        <Stack className={`${styles.answerContainer} ${isSelected && styles.selected}`} verticalAlign="space-between">
            <Stack.Item>
                <Stack horizontal horizontalAlign="space-between">
                    <AnswerIcon />
                    <div>
                        <IconButton
                            style={{ color: "black" }}
                            iconProps={{ iconName: "Lightbulb" }}
                            title="Show thought process"
                            ariaLabel="Show thought process"
                            onClick={() => onThoughtProcessClicked()}
                            disabled={!answer.choices[0].context.thoughts?.length}
                        />
                        <IconButton
                            style={{ color: "black" }}
                            iconProps={{ iconName: "ClipboardList" }}
                            title="Show supporting content"
                            ariaLabel="Show supporting content"
                            onClick={() => onSupportingContentClicked()}
                            disabled={!answer.choices[0].context.data_points}
                        />
                        <IconButton
                            style={{ color: "black" }}
                            iconProps={{ iconName: "BarChart4" }}
                            title="Show Evaluation"
                            ariaLabel="Show Evaluation"
                            onClick={() => onEvaluationClicked()}
                            disabled={!answer.choices[0].context.data_points}
                        />
                    </div>
                </Stack>
            </Stack.Item>

            <Stack.Item grow>
                <div className={styles.answerText} dangerouslySetInnerHTML={{ __html: sanitizedAnswerHtml }}></div>
            </Stack.Item>

            {!!parsedAnswer.citations.length && (
                <Stack.Item>
                    <Stack horizontal wrap tokens={{ childrenGap: 5 }}>
                        <span className={styles.citationLearnMore}>Citations:</span>
                        {parsedAnswer.citations.map((x, i) => {
                            const path = getCitationFilePath(x);
                            return (
                                <a key={i} className={styles.citation} title={x} onClick={() => onCitationClicked(path)}>
                                    {`${++i}. ${x}`}
                                </a>
                            );
                        })}
                    </Stack>
                </Stack.Item>
            )}

            {!!followupQuestions?.length && showFollowupQuestions && onFollowupQuestionClicked && (
                <Stack.Item>
                    <Stack horizontal wrap className={`${!!parsedAnswer.citations.length ? styles.followupQuestionsList : ""}`} tokens={{ childrenGap: 6 }}>
                        <span className={styles.followupQuestionLearnMore}>Follow-up questions:</span>
                        {followupQuestions.map((x, i) => {
                            return (
                                <a key={i} className={styles.followupQuestion} title={x} onClick={() => onFollowupQuestionClicked(x)}>
                                    {`${x}`}
                                </a>
                            );
                        })}
                    </Stack>
                </Stack.Item>
            )}

            <Stack.Item>
                {feedbackGiven ? (
                    <div className={styles.satisfactionContainer}>
                        <span className={styles.satisfactory}>Thank you for your feedback!</span>
                    </div>
                ) : (
                    <div className={styles.satisfactionContainer}>
                        <span className={styles.satisfactory}>Did you like this response?</span>
                        <IconButton
                            style={{ color: "green" }}
                            iconProps={{ iconName: "CheckMark" }}
                            title="Show thought process"
                            ariaLabel="Show thought process"
                            onClick={() => onGoodFeedbackClicked()}
                            disabled={!answer.choices[0].context.thoughts?.length}
                        />
                        <IconButton
                            style={{ color: "red" }}
                            iconProps={{ iconName: "Cancel" }}
                            title="Show supporting content"
                            ariaLabel="Show supporting content"
                            onClick={() => onBadFeedbackClicked()}
                            disabled={!answer.choices[0].context.data_points}
                        />
                    </div>
                )}
            </Stack.Item>
        </Stack>
    );
};

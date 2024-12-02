import { FeedbackDialog } from "@/components/feedback-dialog";
import { FeedbackTable } from "@/components/feedback-table";

export default function FeedbackPage() {
  return (
    <div>
      <FeedbackDialog feature="dp1" />
      <FeedbackTable feature="dp1" />
    </div>
  );
}

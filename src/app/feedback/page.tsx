import { FeedbackDialog } from "@/components/feedback-dialog";
import { FeedbackTable } from "@/components/feedback-table";

export default function FeedbackPage() {
  return (
    <div>
      <FeedbackDialog />
      <FeedbackTable />
    </div>
  );
}

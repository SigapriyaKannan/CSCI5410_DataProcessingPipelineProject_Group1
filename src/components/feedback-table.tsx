"use client";

import React, { useState, useEffect } from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

// Define the type for feedback sentiment
interface FeedbackSentiment {
  id: string;
  feedback: string;
  feature: string;
  timestamp: string;
  sentiment_score: number;
  sentiment_magnitude: number;
}

interface FeedbackTableProps {
  feature: string;
}

export function FeedbackTable({ feature }: FeedbackTableProps) {
  const [feedbacks, setFeedbacks] = useState<FeedbackSentiment[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedFeedback, setSelectedFeedback] =
    useState<FeedbackSentiment | null>(null);

  // Function to fetch feedbacks
  const fetchFeedbackSentiments = async () => {
    try {
      setIsLoading(true);
      const response = await fetch(
        `https://us-central1-k8s-assignment-csci5409.cloudfunctions.net/get-feedbacks?feature=${feature}`,
      );

      if (!response.ok) {
        throw new Error("Failed to fetch feedback sentiments");
      }

      const data = await response.json();
      setFeedbacks(data);
      setError(null);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "An unknown error occurred",
      );
      setFeedbacks([]);
    } finally {
      setIsLoading(false);
    }
  };

  // Fetch feedbacks on component mount
  useEffect(() => {
    fetchFeedbackSentiments();
  }, []);

  // Determine sentiment label and color
  const getSentimentLabel = (score: number) => {
    if (score < -0.25) return "Negative";
    if (score > 0.25) return "Positive";
    return "Neutral";
  };

  const getSentimentVariant = (score: number) => {
    if (score < -0.25) return "destructive";
    if (score > 0.25) return "default";
    return "secondary";
  };

  // Render loading state
  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <p>Loading feedback sentiments...</p>
      </div>
    );
  }

  // Render error state
  if (error) {
    return (
      <div className="flex justify-center items-center h-64 text-red-500">
        <p>Error: {error}</p>
        <Button onClick={fetchFeedbackSentiments} className="ml-4">
          Retry
        </Button>
      </div>
    );
  }

  // Render empty state
  if (feedbacks.length === 0) {
    return (
      <div className="flex justify-center items-center h-64">
        <p>No feedback sentiments found.</p>
      </div>
    );
  }

  return (
    <>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Timestamp</TableHead>
            <TableHead>Feedback</TableHead>
            <TableHead>Feature</TableHead>
            <TableHead>Sentiment</TableHead>
            <TableHead>Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {feedbacks.map((feedback) => (
            <TableRow key={feedback.id}>
              <TableCell>
                {new Date(feedback.timestamp).toLocaleString()}
              </TableCell>
              <TableCell className="text-wrap max-w-screen-sm">
                {feedback.feedback}
              </TableCell>
              <TableCell>{feedback.feature}</TableCell>
              <TableCell>
                <Badge
                  variant={getSentimentVariant(feedback.sentiment_score)}
                  className="px-2 py-1"
                >
                  {getSentimentLabel(feedback.sentiment_score)}
                </Badge>
              </TableCell>
              <TableCell>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setSelectedFeedback(feedback)}
                >
                  View Details
                </Button>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>

      {/* Feedback Details Dialog */}
      <Dialog
        open={!!selectedFeedback}
        onOpenChange={() => setSelectedFeedback(null)}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Feedback Details</DialogTitle>
            <DialogDescription>Sentiment Analysis Results</DialogDescription>
          </DialogHeader>
          {selectedFeedback && (
            <div className="space-y-4">
              <div>
                <p className="font-semibold">Feedback:</p>
                <p>{selectedFeedback.feedback}</p>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="font-semibold">Sentiment Score:</p>
                  <Badge
                    variant={getSentimentVariant(
                      selectedFeedback.sentiment_score,
                    )}
                  >
                    {selectedFeedback.sentiment_score.toFixed(2)}
                  </Badge>
                </div>
                <div>
                  <p className="font-semibold">Sentiment Magnitude:</p>
                  <Badge variant="secondary">
                    {selectedFeedback.sentiment_magnitude.toFixed(2)}
                  </Badge>
                </div>
              </div>
              <div>
                <p className="font-semibold">Timestamp:</p>
                <p>{new Date(selectedFeedback.timestamp).toLocaleString()}</p>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </>
  );
}

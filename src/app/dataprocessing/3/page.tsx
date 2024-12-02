'use client'

import { useState, useEffect, useCallback, useContext } from 'react';
import { useDropzone } from 'react-dropzone';
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Loader2 } from 'lucide-react';
import { FileHistory } from '@/components/file-history-dp3';
import { FeedbackTable } from '@/components/feedback-table';
import { FeedbackDialog } from '@/components/feedback-dialog';
import { UserContext } from '@/app/contexts/user-context';
interface FileDetails {
  fileName: string;
  referenceId: string;
  fileSize: string,
  timestamp: string;
  status: string;
  url: string;
}

export default function FileUploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [fileHistory, setFileHistory] = useState<FileDetails[]>([]);
  const [isFetching, setIsFetching] = useState(true);
  const { user } = useContext(UserContext);

  // Fetch file history
  useEffect(() => {
    const fetchFileHistory = async () => {
      try {
        const userInfo = JSON.parse(localStorage.getItem('user') || '{}');
        const email = userInfo.email;

        const getAllJobsRequest = {
          user_email: email,
        };

        const response = await fetch(
          `https://cp4fm5iznqaqvnk6vkmwleqqcq0vadfs.lambda-url.us-east-1.on.aws/`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify(getAllJobsRequest),
          }
        );

        if (response.ok) {
          const data = await response.json();

          // Map API response to match the FileDetails type
          const formattedFiles = data.map((file: any): FileDetails => ({
            fileName: file.filename,
            referenceId: file.process_code ?? '-',
            timestamp: file.Timestamp
              ? new Date(file.Timestamp * 1000).toISOString()
              : '-',
            url: file.Url ?? '-',
            status: "SUCCEEDED",
            fileSize: file.file_size?.toString() ?? '-',
          }));

          console.log(formattedFiles);
          // Sort by timestamp in descending order
          formattedFiles.sort(
            (a: any, b: any) =>
              new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
          );

          setFileHistory(formattedFiles);
        } else {
          console.error('Error fetching file history:', await response.text());
        }
      } catch (error) {
        console.error('Error:', error);
      } finally {
        setIsFetching(false);
      }
    };

    fetchFileHistory();
  }, []);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles && acceptedFiles.length > 0) {
      setFile(acceptedFiles[0]);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop });

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files.length > 0) {
      setFile(event.target.files[0]);
    }
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!file) return;

    setIsLoading(true);

    try {
      const userInfo = JSON.parse(localStorage.getItem('user') || '{}');
      const email = userInfo.email;
      const role = userInfo.role;
      const accessToken = userInfo.accessToken;

      const formData = new FormData();
      formData.append('file', file);
      formData.append('email', email);
      formData.append('role', role);

      const response = await fetch(
        `https://rq4cw65uq3ywwa5rylp3yfmkly0cngqw.lambda-url.us-east-1.on.aws/`,
        {
          method: 'POST',
          body: formData,
        }
      );

      if (response.ok) {
        const updatedFile = await response.json();

        const formattedFile: FileDetails = {
          fileName: '-',
          referenceId: updatedFile.process_code ?? '-',
          timestamp: new Date().toISOString(),
          url: '-',
          fileSize: '-',
          status: 'PROCESSING',
        };

        setFileHistory((prev) => [formattedFile, ...prev]);
      } else {
        console.error('Error uploading file:', await response.text());
      }
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setIsLoading(false);
      setFile(null);
    }
  };

  if (isFetching) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="h-6 w-6 animate-spin" />
        <span className="ml-2">Loading...</span>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-6 py-8 min-h-screen">
      <div className="space-y-8">
        <Card className="w-full">
          <CardContent className="pt-6">
            <h2 className="text-2xl font-bold text-center mb-6">File Upload</h2>
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Drag-and-Drop Area */}
              <div
                {...getRootProps()}
                className={`p-6 border-2 border-dashed rounded-lg cursor-pointer transition-colors ${
                  isDragActive ? 'border-primary bg-primary/10' : 'border-gray-300 hover:border-primary/50'
                }`}
              >
                <input {...getInputProps()} />
                <p className="text-center">
                  {isDragActive ? (
                    <span className="text-primary">Drop the file here...</span>
                  ) : (
                    'Drag & drop a file here, or click to select one'
                  )}
                </p>
              </div>

              {/* File Selection Status */}
              <div className="text-sm text-muted-foreground text-center">
                {file ? `Selected file: ${file.name}` : 'No file selected'}
              </div>

              {/* File Upload Input */}
              <div className="relative flex items-center justify-center">
                <label className="bg-primary text-primary-foreground py-2 px-4 rounded-lg cursor-pointer hover:bg-primary/90">
                  Choose File
                  <input
                    type="file"
                    onChange={handleFileChange}
                    className="hidden"
                  />
                </label>
              </div>

              {/* Submit Button */}
              <Button type="submit" className="w-full" disabled={!file || isLoading}>
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Processing
                  </>
                ) : (
                  'Submit'
                )}
              </Button>
            </form>
          </CardContent>
        </Card>

        {/* File History Section */}
        <FileHistory files={fileHistory} />

        {/* Feedback Section */}
        <FeedbackTable feature="dp3" />
        { user && user.role === "Registered" && <FeedbackDialog feature="dp3" />}
      </div>
    </div>
  );
}
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Button } from "@/components/ui/button";

interface FileDetails {
  fileName: string;
  referenceId: string;
  timestamp: string;
  txtFileLink: string;
  rowCount: string;
  status: string;
}

interface FileHistoryProps {
  files: FileDetails[];
}

export function FileHistory({ files }: FileHistoryProps) {
  const getStatusColor = (status: string) => {
    switch (status.toUpperCase()) {
      case 'SUCCEEDED':
        return 'text-green-500';
      case 'FAILED':
        return 'text-red-500';
      case 'RUNNING':
        return 'text-blue-500';
      default:
        return 'text-gray-500';
    }
  };

  const formatDate = (timestamp: string): string => {
    const date = new Date(timestamp);
    return isNaN(date.getTime()) ? '-' : date.toLocaleString();
  };

  return (
    <div>
      <h3 className="text-xl font-bold mb-4">File History</h3>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Reference ID</TableHead>
            <TableHead>Timestamp</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Download</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {files.map((file) => (
            <TableRow key={file.referenceId}>
              <TableCell>{file.referenceId}</TableCell>
              <TableCell>{formatDate(file.timestamp)}</TableCell>
              <TableCell>
                <span className={`font-bold ${getStatusColor(file.status)}`}>{file.status}</span>
              </TableCell>
              <TableCell>
                {file.status.toUpperCase() === 'SUCCEEDED' ? (
                  <Button variant="link" asChild>
                    <a href={file.txtFileLink} target="_blank" rel="noopener noreferrer">
                      Download
                    </a>
                  </Button>
                ) : (
                  '-'
                )}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
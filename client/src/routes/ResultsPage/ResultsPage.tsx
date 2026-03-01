import { useState, useEffect } from "react";
import { api, ResultItem } from "@/services/api";
import { Loader2, FileImage, Clock, ChevronLeft, ChevronRight, AlertTriangle } from "lucide-react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

const fallbackLabels: Record<string, string> = {
  heuristic: "Heuristic",
  brightness: "Brightness",
  raw: "Raw",
  default: "Default",
};

export default function ResultsPage() {
  const [results, setResults] = useState<ResultItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedResult, setSelectedResult] = useState<ResultItem | null>(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  useEffect(() => {
    fetchResults();
  }, [page]);

  const fetchResults = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await api.getResults(page);
      setResults(response.results);
      setTotalPages(response.total_pages);
    } catch {
      setError("Failed to load results. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const formatLabel = (label: string): string => {
    return label
      .split("_")
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ");
  };

  const formatTimestamp = (timestamp: string): string => {
    const date = new Date(timestamp);
    return date.toLocaleString(undefined, {
      dateStyle: "medium",
      timeStyle: "short",
    });
  };

  const getTopPredictions = (predictions: ResultItem["predictions"]): string => {
    const sorted = [...predictions].sort((a, b) => b.confidence - a.confidence);
    return sorted
      .slice(0, 3)
      .map((p) => formatLabel(p.label))
      .join(", ");
  };

  if (isLoading) {
    return (
      <section className="mx-auto w-full max-w-3xl rounded-xl border bg-card p-6 shadow-sm">
        <div className="flex flex-col items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
          <p className="mt-4 text-sm text-muted-foreground">
            Loading results...
          </p>
        </div>
      </section>
    );
  }

  if (error) {
    return (
      <section className="mx-auto w-full max-w-3xl rounded-xl border bg-card p-6 shadow-sm">
        <div className="mb-6">
          <h1 className="text-2xl font-semibold tracking-tight">Results</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            View your past analysis results.
          </p>
        </div>
        <div className="rounded-md bg-destructive/10 p-4 text-sm text-destructive">
          {error}
        </div>
        <Button variant="outline" className="mt-4" onClick={fetchResults}>
          Try Again
        </Button>
      </section>
    );
  }

  return (
    <section className="mx-auto w-full max-w-3xl rounded-xl border bg-card p-6 shadow-sm">
      <div className="mb-6">
        <h1 className="text-2xl font-semibold tracking-tight">Results</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          View your past analysis results.
        </p>
      </div>

      {results.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-12 text-center">
          <div className="flex h-16 w-16 items-center justify-center rounded-full bg-muted">
            <FileImage className="h-8 w-8 text-muted-foreground" />
          </div>
          <p className="mt-4 text-lg font-medium">No results yet</p>
          <p className="mt-1 text-sm text-muted-foreground">
            Upload an image to analyze atmospheric phenomena.
          </p>
        </div>
      ) : (
        <>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Filename</TableHead>
                <TableHead>Date</TableHead>
                <TableHead>Top Predictions</TableHead>
                <TableHead>Method</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {results.map((result) => (
                <TableRow
                  key={result.id}
                  className="cursor-pointer"
                  onClick={() => setSelectedResult(result)}
                >
                  <TableCell className="font-medium">
                    {result.original_filename}
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <Clock className="h-4 w-4 text-muted-foreground" />
                      {formatTimestamp(result.timestamp)}
                    </div>
                  </TableCell>
                  <TableCell className="text-muted-foreground">
                    {getTopPredictions(result.predictions)}
                  </TableCell>
                  <TableCell>
                    {result.fallback_method ? (
                      <Badge variant="outline" className="gap-1 text-xs">
                        <AlertTriangle className="h-3 w-3" />
                        {fallbackLabels[result.fallback_method] || result.fallback_method}
                      </Badge>
                    ) : (
                      <span className="text-xs text-muted-foreground">Primary</span>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>

          {totalPages > 1 && (
            <div className="mt-4 flex items-center justify-between">
              <Button
                variant="outline"
                size="sm"
                disabled={page === 1}
                onClick={() => setPage((p) => p - 1)}
              >
                <ChevronLeft className="h-4 w-4" />
                Previous
              </Button>
              <span className="text-sm text-muted-foreground">
                Page {page} of {totalPages}
              </span>
              <Button
                variant="outline"
                size="sm"
                disabled={page === totalPages}
                onClick={() => setPage((p) => p + 1)}
              >
                Next
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          )}
        </>
      )}

      <Dialog open={!!selectedResult} onOpenChange={() => setSelectedResult(null)}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>{selectedResult?.original_filename}</DialogTitle>
            <DialogDescription>
              {selectedResult && formatTimestamp(selectedResult.timestamp)}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground">
                Processing time: {selectedResult?.processing_time_ms}ms
              </span>
              {selectedResult?.fallback_method && (
                <Badge variant="outline" className="gap-1">
                  <AlertTriangle className="h-3 w-3" />
                  {fallbackLabels[selectedResult.fallback_method] || selectedResult.fallback_method} fallback
                </Badge>
              )}
            </div>
            <div className="space-y-4">
              <h3 className="font-semibold">Predictions</h3>
              {selectedResult?.predictions
                .sort((a, b) => b.confidence - a.confidence)
                .map((prediction, index) => (
                  <div key={index} className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="font-medium">
                        {formatLabel(prediction.label)}
                      </span>
                      <span className="text-sm text-muted-foreground">
                        {(prediction.confidence * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className="h-2 w-full overflow-hidden rounded-full bg-muted">
                      <div
                        className="h-full bg-primary transition-all"
                        style={{ width: `${prediction.confidence * 100}%` }}
                      />
                    </div>
                  </div>
                ))}
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </section>
  );
}

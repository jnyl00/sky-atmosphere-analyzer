import { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import axios from "axios";
import { Upload, Image as ImageIcon, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { api, AnalyzeResponse } from "@/services/api";

export default function UploadPage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<AnalyzeResponse | null>(null);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (file) {
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      setError(null);
      setResults(null);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "image/jpeg": [".jpg", ".jpeg"],
      "image/png": [".png"],
    },
    maxSize: 5 * 1024 * 1024,
    multiple: false,
  });

  const handleUpload = async () => {
    if (!selectedFile) return;

    setIsLoading(true);
    setError(null);
    setResults(null);

    try {
      const response = await api.analyze(selectedFile);
      setResults(response);
    } catch (err) {
      if (axios.isAxiosError(err)) {
        const status = err.response?.status;
        const detail = err.response?.data?.detail;

        if (status === 413) {
          setError("File too large. Maximum size: 5MB");
        } else if (status === 415) {
          setError("Unsupported file type. Allowed: image/jpeg, image/png");
        } else if (status === 400) {
          setError(detail || "Invalid or corrupted image file");
        } else {
          setError(detail || "An error occurred during upload");
        }
      } else {
        setError("An unexpected error occurred");
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setSelectedFile(null);
    setPreviewUrl(null);
    setError(null);
    setResults(null);
  };

  const formatLabel = (label: string): string => {
    return label
      .split("_")
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ");
  };

  return (
    <section className="mx-auto w-full max-w-3xl rounded-xl border bg-card p-6 shadow-sm">
      <div className="mb-6">
        <h1 className="text-2xl font-semibold tracking-tight">Upload</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Upload an image to analyze atmospheric phenomena.
        </p>
      </div>

      {!results ? (
        <>
          <div
            {...getRootProps()}
            className={`mb-6 flex cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed p-8 transition-colors ${
              isDragActive
                ? "border-primary bg-primary/5"
                : "border-border hover:border-primary/50"
            }`}
          >
            <input {...getInputProps()} />
            {previewUrl ? (
              <div className="flex flex-col items-center gap-4">
                <img
                  src={previewUrl}
                  alt="Preview"
                  className="max-h-64 rounded-md object-contain"
                />
                <p className="text-sm text-muted-foreground">
                  {selectedFile?.name}
                </p>
              </div>
            ) : (
              <div className="flex flex-col items-center gap-4 text-center">
                <div className="flex h-16 w-16 items-center justify-center rounded-full bg-muted">
                  <Upload className="h-8 w-8 text-muted-foreground" />
                </div>
                <div>
                  <p className="text-lg font-medium">
                    {isDragActive
                      ? "Drop the image here"
                      : "Drag & drop an image here"}
                  </p>
                  <p className="mt-1 text-sm text-muted-foreground">
                    or click to select a file
                  </p>
                </div>
                <p className="text-xs text-muted-foreground">
                  Supported: JPEG, PNG (max 5MB)
                </p>
              </div>
            )}
          </div>

          {error && (
            <div className="mb-4 rounded-md bg-destructive/10 p-4 text-sm text-destructive">
              {error}
            </div>
          )}

          {selectedFile && (
            <div className="flex gap-4">
              <Button onClick={handleUpload} disabled={isLoading} className="flex-1">
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <ImageIcon className="mr-2 h-4 w-4" />
                    Analyze Image
                  </>
                )}
              </Button>
              <Button variant="outline" onClick={handleReset}>
                Clear
              </Button>
            </div>
          )}
        </>
      ) : (
        <div className="space-y-6">
          <div className="flex flex-col items-center gap-4">
            <img
              src={previewUrl!}
              alt="Analyzed"
              className="max-h-64 rounded-md object-contain"
            />
            <p className="text-sm text-muted-foreground">
              Processing time: {results.processing_time_ms}ms
            </p>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Predictions</CardTitle>
              <CardDescription>
                Detected atmospheric phenomena
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {results.predictions
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
            </CardContent>
            <CardFooter>
              <Button variant="outline" className="w-full" onClick={handleReset}>
                Upload Another Image
              </Button>
            </CardFooter>
          </Card>
        </div>
      )}
    </section>
  );
}

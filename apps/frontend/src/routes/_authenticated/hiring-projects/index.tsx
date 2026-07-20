import { useState } from 'react';
import { createFileRoute, Link } from '@tanstack/react-router';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  createHiringProject,
  listHiringProjects,
} from '@/features/hiring-projects/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { RichTextEditor } from '@/components/rich-text-editor';
import { RichTextContent } from '@/components/rich-text-content';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';

export const Route = createFileRoute('/_authenticated/hiring-projects/')({
  component: HiringProjectsPage,
});

function HiringProjectsPage() {
  const { data: projects, isLoading } = useQuery({
    queryKey: ['hiring-projects'],
    queryFn: listHiringProjects,
  });

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Hiring Projects</h1>
        <CreateHiringProjectDialog />
      </div>

      {isLoading && <p className="text-muted-foreground">Loading…</p>}

      <div className="grid gap-4 sm:grid-cols-2">
        {projects?.map((project) => (
          <Link
            key={project.id}
            to="/hiring-projects/$projectId"
            params={{ projectId: String(project.id) }}>
            <Card className="h-full transition hover:shadow-md">
              <CardHeader>
                <div className="flex items-center justify-between gap-2">
                  <CardTitle>{project.title}</CardTitle>
                  <Badge
                    variant={
                      project.status === 'open' ? 'default' : 'secondary'
                    }>
                    {project.status}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <RichTextContent
                  html={project.job_description}
                  className="line-clamp-3 text-muted-foreground **:my-0!"
                />
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  );
}

function CreateHiringProjectDialog() {
  const queryClient = useQueryClient();
  const [open, setOpen] = useState(false);
  const [title, setTitle] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  // Bump to remount (and reset) the uncontrolled editor after a successful create.
  const [editorKey, setEditorKey] = useState(0);

  const mutation = useMutation({
    mutationFn: () =>
      createHiringProject({ title, job_description: jobDescription }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['hiring-projects'] });
      setOpen(false);
      setTitle('');
      setJobDescription('');
      setEditorKey((k) => k + 1);
    },
  });

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger render={<Button>New hiring project</Button>} />
      <DialogContent className={'sm:min-w-xl max-h-[90vh] overflow-auto'}>
        <DialogHeader>
          <DialogTitle>Create hiring project</DialogTitle>
        </DialogHeader>
        <form
          className="flex flex-col gap-4"
          onSubmit={(e) => {
            e.preventDefault();
            mutation.mutate();
          }}>
          <div className="flex flex-col gap-2">
            <Label htmlFor="title">Title</Label>
            <Input
              id="title"
              required
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Enter the title of the hiring project"
            />
          </div>
          <div className="flex flex-col gap-2">
            <Label>Job description</Label>
            <RichTextEditor
              key={editorKey}
              onChange={setJobDescription}
              placeholder="Describe the role, responsibilities, and requirements…"
            />
          </div>
          <Button
            type="submit"
            disabled={mutation.isPending || jobDescription.trim() === ''}>
            {mutation.isPending ? 'Creating…' : 'Create'}
          </Button>
        </form>
      </DialogContent>
    </Dialog>
  );
}

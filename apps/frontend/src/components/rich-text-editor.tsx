import { useCallback, useEffect, useState } from 'react'
import { LexicalComposer } from '@lexical/react/LexicalComposer'
import { RichTextPlugin } from '@lexical/react/LexicalRichTextPlugin'
import { ContentEditable } from '@lexical/react/LexicalContentEditable'
import { HistoryPlugin } from '@lexical/react/LexicalHistoryPlugin'
import { ListPlugin } from '@lexical/react/LexicalListPlugin'
import { OnChangePlugin } from '@lexical/react/LexicalOnChangePlugin'
import { LexicalErrorBoundary } from '@lexical/react/LexicalErrorBoundary'
import { useLexicalComposerContext } from '@lexical/react/LexicalComposerContext'
import { $generateHtmlFromNodes, $generateNodesFromDOM } from '@lexical/html'
import {
  $isListNode,
  INSERT_ORDERED_LIST_COMMAND,
  INSERT_UNORDERED_LIST_COMMAND,
  ListItemNode,
  ListNode,
  REMOVE_LIST_COMMAND,
} from '@lexical/list'
import {
  $createHeadingNode,
  $isHeadingNode,
  HeadingNode,
  type HeadingTagType,
} from '@lexical/rich-text'
import { $setBlocksType } from '@lexical/selection'
import { $getNearestNodeOfType, mergeRegister } from '@lexical/utils'
import {
  $createParagraphNode,
  $getRoot,
  $getSelection,
  $isElementNode,
  $isRangeSelection,
  CAN_REDO_COMMAND,
  CAN_UNDO_COMMAND,
  FORMAT_TEXT_COMMAND,
  REDO_COMMAND,
  SELECTION_CHANGE_COMMAND,
  UNDO_COMMAND,
} from 'lexical'
import type { EditorState, LexicalEditor } from 'lexical'
import {
  Bold,
  Heading2,
  Heading3,
  Italic,
  List,
  ListOrdered,
  Pilcrow,
  Redo2,
  Undo2,
} from 'lucide-react'
import { cn } from '@/lib/utils'

type BlockType = 'paragraph' | 'h2' | 'h3' | 'ul' | 'ol'

const theme = {
  paragraph: 'mb-2 last:mb-0',
  heading: { h2: 'mt-4 mb-2 text-lg font-semibold', h3: 'mt-3 mb-1 text-base font-semibold' },
  list: {
    ul: 'my-2 list-disc pl-6',
    ol: 'my-2 list-decimal pl-6',
    listitem: 'mb-1',
    nested: { listitem: 'list-none' },
  },
  text: { bold: 'font-semibold', italic: 'italic' },
}

/** Load an HTML string into the editor once, wrapping loose inline nodes in paragraphs. */
function $initFromHtml(editor: LexicalEditor, html: string) {
  const root = $getRoot()
  root.clear()
  if (html.trim()) {
    const dom = new DOMParser().parseFromString(html, 'text/html')
    const nodes = $generateNodesFromDOM(editor, dom)
    let paragraph: ReturnType<typeof $createParagraphNode> | null = null
    for (const node of nodes) {
      if ($isElementNode(node) && !node.isInline()) {
        if (paragraph) {
          root.append(paragraph)
          paragraph = null
        }
        root.append(node)
      } else {
        paragraph ??= $createParagraphNode()
        paragraph.append(node)
      }
    }
    if (paragraph) root.append(paragraph)
  }
  if (root.getChildrenSize() === 0) root.append($createParagraphNode())
}

const iconButton =
  'inline-flex size-8 items-center justify-center rounded-md text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground disabled:pointer-events-none disabled:opacity-40'

function ToolbarButton({
  active,
  disabled,
  onClick,
  label,
  children,
}: {
  active?: boolean
  disabled?: boolean
  onClick: () => void
  label: string
  children: React.ReactNode
}) {
  return (
    <button
      type="button"
      aria-label={label}
      title={label}
      aria-pressed={active}
      disabled={disabled}
      // Keep editor focus/selection when clicking a toolbar button.
      onMouseDown={(e) => e.preventDefault()}
      onClick={onClick}
      className={cn(iconButton, active && 'bg-accent text-accent-foreground')}
    >
      {children}
    </button>
  )
}

function Toolbar() {
  const [editor] = useLexicalComposerContext()
  const [blockType, setBlockType] = useState<BlockType>('paragraph')
  const [isBold, setIsBold] = useState(false)
  const [isItalic, setIsItalic] = useState(false)
  const [canUndo, setCanUndo] = useState(false)
  const [canRedo, setCanRedo] = useState(false)

  const updateToolbar = useCallback(() => {
    const selection = $getSelection()
    if (!$isRangeSelection(selection)) return
    setIsBold(selection.hasFormat('bold'))
    setIsItalic(selection.hasFormat('italic'))

    const anchorNode = selection.anchor.getNode()
    const element =
      anchorNode.getKey() === 'root'
        ? anchorNode
        : anchorNode.getTopLevelElementOrThrow()
    const listNode = $getNearestNodeOfType(anchorNode, ListNode)
    if (listNode && $isListNode(listNode)) {
      setBlockType(listNode.getListType() === 'number' ? 'ol' : 'ul')
    } else if ($isHeadingNode(element)) {
      setBlockType(element.getTag() === 'h3' ? 'h3' : 'h2')
    } else {
      setBlockType('paragraph')
    }
  }, [])

  useEffect(() => {
    return mergeRegister(
      editor.registerUpdateListener(({ editorState }) => {
        editorState.read(updateToolbar)
      }),
      editor.registerCommand(
        SELECTION_CHANGE_COMMAND,
        () => {
          updateToolbar()
          return false
        },
        1,
      ),
      editor.registerCommand(CAN_UNDO_COMMAND, (payload) => {
        setCanUndo(payload)
        return false
      }, 1),
      editor.registerCommand(CAN_REDO_COMMAND, (payload) => {
        setCanRedo(payload)
        return false
      }, 1),
    )
  }, [editor, updateToolbar])

  const toBlock = (target: 'paragraph' | 'h2' | 'h3') => {
    editor.update(() => {
      const selection = $getSelection()
      if (!$isRangeSelection(selection)) return
      $setBlocksType(selection, () =>
        target === 'paragraph'
          ? $createParagraphNode()
          : $createHeadingNode(target as HeadingTagType),
      )
    })
  }

  const toggleList = (type: 'ul' | 'ol') => {
    if (blockType === type) {
      editor.dispatchCommand(REMOVE_LIST_COMMAND, undefined)
    } else if (type === 'ul') {
      editor.dispatchCommand(INSERT_UNORDERED_LIST_COMMAND, undefined)
    } else {
      editor.dispatchCommand(INSERT_ORDERED_LIST_COMMAND, undefined)
    }
  }

  return (
    <div className="flex flex-wrap items-center gap-0.5 border-b border-input p-1">
      <ToolbarButton
        label="Bold"
        active={isBold}
        onClick={() => editor.dispatchCommand(FORMAT_TEXT_COMMAND, 'bold')}
      >
        <Bold className="size-4" />
      </ToolbarButton>
      <ToolbarButton
        label="Italic"
        active={isItalic}
        onClick={() => editor.dispatchCommand(FORMAT_TEXT_COMMAND, 'italic')}
      >
        <Italic className="size-4" />
      </ToolbarButton>
      <span className="mx-1 h-5 w-px bg-border" />
      <ToolbarButton
        label="Paragraph"
        active={blockType === 'paragraph'}
        onClick={() => toBlock('paragraph')}
      >
        <Pilcrow className="size-4" />
      </ToolbarButton>
      <ToolbarButton
        label="Heading 2"
        active={blockType === 'h2'}
        onClick={() => toBlock('h2')}
      >
        <Heading2 className="size-4" />
      </ToolbarButton>
      <ToolbarButton
        label="Heading 3"
        active={blockType === 'h3'}
        onClick={() => toBlock('h3')}
      >
        <Heading3 className="size-4" />
      </ToolbarButton>
      <span className="mx-1 h-5 w-px bg-border" />
      <ToolbarButton
        label="Bulleted list"
        active={blockType === 'ul'}
        onClick={() => toggleList('ul')}
      >
        <List className="size-4" />
      </ToolbarButton>
      <ToolbarButton
        label="Numbered list"
        active={blockType === 'ol'}
        onClick={() => toggleList('ol')}
      >
        <ListOrdered className="size-4" />
      </ToolbarButton>
      <span className="mx-1 h-5 w-px bg-border" />
      <ToolbarButton
        label="Undo"
        disabled={!canUndo}
        onClick={() => editor.dispatchCommand(UNDO_COMMAND, undefined)}
      >
        <Undo2 className="size-4" />
      </ToolbarButton>
      <ToolbarButton
        label="Redo"
        disabled={!canRedo}
        onClick={() => editor.dispatchCommand(REDO_COMMAND, undefined)}
      >
        <Redo2 className="size-4" />
      </ToolbarButton>
    </div>
  )
}

/** Bridges Lexical's onChange to an HTML string, ignoring selection-only changes. */
function HtmlOnChangePlugin({ onChange }: { onChange: (html: string) => void }) {
  const handleChange = useCallback(
    (editorState: EditorState, editor: LexicalEditor) => {
      editorState.read(() => {
        const root = $getRoot()
        // Emit empty string when the document has no text, so callers can validate.
        const html = root.getTextContent().trim() ? $generateHtmlFromNodes(editor, null) : ''
        onChange(html)
      })
    },
    [onChange],
  )
  return <OnChangePlugin onChange={handleChange} ignoreSelectionChange />
}

export function RichTextEditor({
  initialHtml = '',
  onChange,
  placeholder = 'Write here…',
  className,
}: {
  initialHtml?: string
  onChange: (html: string) => void
  placeholder?: string
  className?: string
}) {
  return (
    <LexicalComposer
      initialConfig={{
        namespace: 'rich-text-editor',
        theme,
        nodes: [HeadingNode, ListNode, ListItemNode],
        onError: (error) => {
          throw error
        },
        editorState: (editor) => $initFromHtml(editor, initialHtml),
      }}
    >
      <div
        className={cn(
          'rounded-md border border-input bg-transparent shadow-xs focus-within:ring-1 focus-within:ring-ring',
          className,
        )}
      >
        <Toolbar />
        <div className="relative">
          <RichTextPlugin
            contentEditable={
              <ContentEditable
                aria-label="Job description"
                className="min-h-32 px-3 py-2 text-sm outline-none [&_a]:underline"
              />
            }
            placeholder={
              <div className="pointer-events-none absolute left-3 top-2 text-sm text-muted-foreground">
                {placeholder}
              </div>
            }
            ErrorBoundary={LexicalErrorBoundary}
          />
        </div>
      </div>
      <HistoryPlugin />
      <ListPlugin />
      <HtmlOnChangePlugin onChange={onChange} />
    </LexicalComposer>
  )
}

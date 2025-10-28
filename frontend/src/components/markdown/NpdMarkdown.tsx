import Markdown from "react-markdown"
import remarkGfm from "remark-gfm"
import { MdComponents } from "./MdComponents"

export const NpdMarkdown = ({ content }: { content: string }) => {
  return (
    <Markdown components={MdComponents} remarkPlugins={[remarkGfm]}>
      {content}
    </Markdown>
  )
}

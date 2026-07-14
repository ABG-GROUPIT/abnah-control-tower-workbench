CREATE TABLE `workspace_documents` (
	`report_id` text PRIMARY KEY NOT NULL,
	`name` text NOT NULL,
	`page` text NOT NULL,
	`section` text NOT NULL,
	`domain` text NOT NULL,
	`workflow_status` text DEFAULT 'draft' NOT NULL,
	`version` integer DEFAULT 1 NOT NULL,
	`is_archived` integer DEFAULT false NOT NULL,
	`payload` text NOT NULL,
	`created_at` text DEFAULT CURRENT_TIMESTAMP NOT NULL,
	`updated_at` text DEFAULT CURRENT_TIMESTAMP NOT NULL,
	`updated_by` text NOT NULL
);
--> statement-breakpoint
CREATE INDEX `workspace_documents_page_section_idx` ON `workspace_documents` (`page`,`section`);--> statement-breakpoint
CREATE INDEX `workspace_documents_workflow_idx` ON `workspace_documents` (`workflow_status`);--> statement-breakpoint
CREATE TABLE `workspace_revisions` (
	`id` text PRIMARY KEY NOT NULL,
	`report_id` text NOT NULL,
	`version` integer NOT NULL,
	`workflow_status` text NOT NULL,
	`action` text NOT NULL,
	`payload` text NOT NULL,
	`actor` text NOT NULL,
	`created_at` text DEFAULT CURRENT_TIMESTAMP NOT NULL
);
--> statement-breakpoint
CREATE UNIQUE INDEX `workspace_revisions_report_version_idx` ON `workspace_revisions` (`report_id`,`version`);--> statement-breakpoint
CREATE INDEX `workspace_revisions_report_created_idx` ON `workspace_revisions` (`report_id`,`created_at`);--> statement-breakpoint
CREATE INDEX `workspace_revisions_published_idx` ON `workspace_revisions` (`report_id`,`workflow_status`);
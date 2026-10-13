
from dataclasses import dataclass, field


@dataclass
class BasicBlock:
    block_id: int
    instructions: list = field(default_factory=list)
    successors: list = field(default_factory=list)


@dataclass
class ControlFlowGraph:
    function_name: str
    blocks: list = field(default_factory=list)
    entry: int = 0
    exit: int = 0


def build_cfg(ir_function):
    """Build a simple sequential CFG from an IR function."""
    cfg = ControlFlowGraph(
        function_name=ir_function.name
    )

    # Create an entry block.
    cfg.blocks.append(BasicBlock(block_id=0))

    # Give each IR instruction its own block.
    for instruction in ir_function.instructions:
        block_id = len(cfg.blocks)

        cfg.blocks.append(
            BasicBlock(
                block_id=block_id,
                instructions=[instruction],
            )
        )

    # Connect blocks in execution order.
    for index in range(len(cfg.blocks) - 1):
        cfg.blocks[index].successors.append(index + 1)

    # Create an exit block.
    exit_id = len(cfg.blocks)
    cfg.blocks.append(BasicBlock(block_id=exit_id))

    # Connect the final instruction block to exit.
    if len(cfg.blocks) >= 2:
        cfg.blocks[-2].successors.append(exit_id)

    cfg.exit = exit_id

    return cfg


def build_program_cfg(ir_program):
    """Build one CFG for each function in an IR program."""
    return [
        build_cfg(function)
        for function in ir_program.functions
    ]
